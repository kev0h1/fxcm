import math
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.config import ForexPairEnum, PeriodEnum, PositionEnum, conversion_map
from src.container.container import Container
from src.domain.trade import Trade
from src.service_layer.indicators import Indicators

from src.service_layer.uow import MongoUnitOfWork
from src.logger import get_logger
from src.entry_points.scheduler.manage_closed_trades import update_trade_state
from src.utils import close_trade_in_oanda_util

logger = get_logger(__name__)


@inject
async def manage_trades_handler(
    uow: MongoUnitOfWork = Depends(Provide[Container.uow]),
    indicator: Indicators = Depends(Provide[Container.indicator_service]),
) -> None:  # type: ignore
    async with uow:
        forex_pairs: list[
            ForexPairEnum
        ] = await uow.trade_repository.get_distinct_forex_pairs()
        for forex_pair in forex_pairs:
            data = await uow.fxcm_connection.get_candle_data(
                forex_pair, PeriodEnum.MINUTE_1, 20
            )
            data = await indicator.get_atr(data, 14)
            close = data.iloc[-1]["close"]
            atr = data.iloc[-1]["atr"]

            trades: list[
                Trade
            ] = await uow.trade_repository.get_open_trades_by_forex_pair(
                forex_pair=forex_pair
            )
            multiplier = 4

            pip_value = (
                0.0001 if "JPY" not in forex_pair.value.split("/") else 0.01
            )

            gbp_per_pip = await calculate_gbp_pips(forex_pair, uow, pip_value)

            for trade in trades:
                modified = False

                half_spread_pips = (
                    trade.half_spread_cost / gbp_per_pip
                ) * pip_value

                if trade.is_buy:
                    adjusted_close_long = close
                    new_stop = adjusted_close_long - multiplier * atr
                    if new_stop > trade.stop and new_stop > (
                        trade.close + half_spread_pips
                    ):
                        # get the pip location =
                        trade.stop = new_stop
                        modified = True
                else:
                    adjusted_close_short = close
                    new_stop = adjusted_close_short + multiplier * atr
                    if new_stop < trade.stop and new_stop < (
                        trade.close - half_spread_pips
                    ):
                        trade.stop = new_stop
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

                if (
                    trade.is_buy
                    and trade.stop > close
                    and trade.stop > trade.close
                ) or (
                    not trade.is_buy
                    and trade.stop < close
                    and trade.stop < trade.close
                ):
                    logger.info(
                        "Trade crossed stop loss for trade %s, with stop of %s and is buy is %s"
                        % (trade.trade_id, trade.stop, trade.is_buy),
                    )
                    trade.position = PositionEnum.CLOSED
                    await close_trade_in_oanda_util(uow, trade)
                    # there reason this didnt work is because you didnt save
                    await uow.trade_repository.save(trade)


async def calculate_gbp_pips(
    forex_pair: ForexPairEnum, uow: MongoUnitOfWork, pip_value: float
) -> float:
    """Calculate the spread pips for a trade"""

    exchange_rate = await uow.fxcm_connection.get_latest_close(
        conversion_map[forex_pair]
    )
    return (100000 * pip_value) / exchange_rate
