import math
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.config import ForexPairEnum
from src.container.container import Container
from src.domain.trade import Trade

from src.service_layer.uow import MongoUnitOfWork
from src.logger import get_logger
from src.utils import count_decimal_places
from src.entry_points.scheduler.manage_closed_trades import update_trade_state

logger = get_logger(__name__)


@inject
async def manage_trades_handler(
    uow: MongoUnitOfWork = Depends(Provide[Container.uow]),
) -> None:  # type: ignore
    async with uow:
        forex_pairs: list[
            ForexPairEnum
        ] = await uow.trade_repository.get_distinct_forex_pairs()
        for forex_pair in forex_pairs:
            close = await uow.fxcm_connection.get_latest_close(forex_pair)
            trades: list[
                Trade
            ] = await uow.trade_repository.get_open_trades_by_forex_pair(
                forex_pair=forex_pair
            )
            currencies = forex_pair.value.split("/")
            pip_value = 0.0001 if "JPY" not in currencies else 0.01
            modified = False

            for trade in trades:
                sl_pips = math.inf if trade.sl_pips is None else trade.sl_pips
                break_even_pips = min(10, sl_pips)
                if trade.is_buy and close > trade.close:
                    diff = round((close - trade.close) / pip_value)
                    if diff >= break_even_pips:
                        if trade.new_close is None:
                            trade.new_close = close
                            trade.stop += break_even_pips * pip_value
                            modified = True

                        else:
                            new_diff = round(
                                (close - trade.new_close) / pip_value
                            )
                            if new_diff >= 1:
                                trade.new_close = close
                                trade.stop += new_diff * pip_value
                                modified = True

                elif not trade.is_buy and close < trade.close:
                    diff = round((trade.close - close) / pip_value)
                    if diff >= break_even_pips:
                        if trade.new_close is None:
                            trade.new_close = close
                            trade.stop -= break_even_pips * pip_value

                            modified = True
                        else:
                            new_diff = round(
                                (trade.new_close - close) / pip_value
                            )
                            if new_diff >= 1:
                                trade.new_close = close
                                trade.stop -= new_diff * pip_value
                                modified = True

                if modified:
                    logger.warning(
                        "Modified trade %s with signal of %s to have a new stop of %s"
                        % (
                            trade.trade_id,
                            trade.is_buy,
                            trade.stop,
                        )
                    )
                    await uow.trade_repository.save(trade)
                if (trade.is_buy and trade.stop > close) or (
                    not trade.is_buy and trade.stop < close
                ):
                    await uow.fxcm_connection.close_trade(
                        trade_id=trade.trade_id,
                        amount=trade.units,
                    )

                    await update_trade_state(uow, trade)
