import math
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.config import ForexPairEnum, PeriodEnum, PositionEnum
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
            multiplier = 3.5
            for trade in trades:
                modified = False

                if trade.is_buy:
                    new_stop = close - multiplier * atr
                    if new_stop > trade.stop:
                        trade.stop = new_stop
                        modified = True
                else:
                    new_stop = close + multiplier * atr
                    if new_stop < trade.stop:
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

                if (trade.is_buy and trade.stop > close) or (
                    not trade.is_buy and trade.stop < close
                ):
                    logger.info(
                        "Trade crossed stop loss for trade %s, with stop of %s and is buy is %s"
                        % (trade.trade_id, trade.stop, trade.is_buy),
                    )
                    trade.position = PositionEnum.CLOSED
                    await close_trade_in_oanda_util(uow, trade)
                    await uow.trade_repository.save(trade)
