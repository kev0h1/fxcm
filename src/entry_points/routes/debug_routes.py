from typing import Any, Union
from fastapi_restful import set_responses, Resource
from src.adapters.database.mongo.mongo_connect import Database
from src.config import CurrencyEnum, ForexPairEnum, PeriodEnum, SentimentEnum
from src.domain.events import CloseTradeEvent
from src.entry_points.scheduler.scheduler import get_fundamental_trend_data
from src.entry_points.scheduler.manage_trades import manage_trades
from src.entry_points.scheduler.get_technical_signal import (
    get_technical_signal,
)
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.container.container import Container
from src.logger import get_logger
from src.service_layer.uow import MongoUnitOfWork
from fastapi import BackgroundTasks
from src.config import DebugEnum
from src.service_layer.handlers import (
    get_trade_parameters,
)
from src.domain.events import OpenTradeEvent

logger = get_logger(__name__)


class DebugResource(Resource):
    @inject
    def __init__(
        self,
        db: Database = Depends(Provide[Container.db]),
        uow: MongoUnitOfWork = Depends(Provide[Container.uow]),
    ) -> None:
        super().__init__()
        self.db = db
        self.uow = uow

    @set_responses(str, 200)
    async def delete(self):
        """Deletes the database"""
        logger.info("Deleting database")
        await self.db.reset_db()
        return "done"

    @set_responses(Any, 200)
    async def put(self, debug_task: DebugEnum):
        """Deletes the database"""
        logger.info("Manually retrieve fundamental data")
        if debug_task == DebugEnum.RunFundamentalEvent:
            await get_fundamental_trend_data()

        if debug_task == DebugEnum.PublishEvent:
            async with self.uow:
                await self.uow.publish(
                    CloseTradeEvent(
                        currency=CurrencyEnum.USD,
                        sentiment=SentimentEnum.BULLISH,
                    )
                )
        if debug_task == DebugEnum.RunIndicatorEvent:
            await get_technical_signal()

        if debug_task == DebugEnum.TestOanda:
            return await self.uow.fxcm_connection.get_candle_data(
                ForexPairEnum.USDJPY, PeriodEnum.MINUTE_5, 100
            )

        if debug_task == DebugEnum.TestOpenTrade:
            data = await self.uow.fxcm_connection.get_candle_data(
                ForexPairEnum.AUDUSD, PeriodEnum.HOUR_1, 100
            )
            close = data["candles"][-1]["mid"]["c"]
            stop = data["candles"][-1]["mid"]["l"]

            event = OpenTradeEvent(
                forex_pair=ForexPairEnum.AUDUSD,
                sentiment=SentimentEnum.BULLISH,
                stop=float(stop),
                close=float(close),
                limit=None,
            )

            is_buy, units = await get_trade_parameters(
                event, self.uow, ForexPairEnum.AUDUSD.value.split("_")
            )

            return await self.uow.fxcm_connection.open_trade(
                instrument=ForexPairEnum.AUDUSD,
                is_buy=is_buy,
                amount=int(20),
                stop=event.stop,
                limit=None,
            )

        if debug_task == DebugEnum.TestCloseTrade:
            return await self.uow.fxcm_connection.close_trade("63", 20)

        if debug_task == DebugEnum.TestGetTrades:
            return await self.uow.fxcm_connection.get_open_positions()

        if debug_task == DebugEnum.TestManageTrade:
            return await manage_trades()

        return "done"


class EventBusRoute(Resource):
    @inject
    def __init__(
        self,
        db: Database = Depends(Provide[Container.db]),
        uow: MongoUnitOfWork = Depends(Provide[Container.uow]),
    ) -> None:
        super().__init__()
        self.db = db
        self.uow = uow

    @set_responses(bool, 200)
    async def get(self):
        """Gets the state of the event bus"""
        logger.info("Getting state of event bus")
        return self.uow.event_bus.running

    @set_responses(str, 200)
    async def post(self, background_tasks: BackgroundTasks):
        """Gets the state of the event bus"""
        logger.info("Getting state of event bus")
        if self.uow.event_bus.running:
            await self.uow.publish(self.uow.event_bus.StopEvent())
            return "stopped"
        else:
            background_tasks.add_task(self.uow.event_bus.start)
            return "started"
