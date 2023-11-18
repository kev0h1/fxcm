import asyncio
from datetime import datetime, timedelta
import os
from typing import Any, Union
from fastapi_restful import set_responses, Resource
from oandapyV20 import V20Error
import pytz
from tzlocal import get_localzone
from src.adapters.database.mongo.mongo_connect import Database
from src.config import (
    CurrencyEnum,
    ForexPairEnum,
    PeriodEnum,
    PositionEnum,
    SentimentEnum,
)
from src.domain.events import CloseTradeEvent
from src.entry_points.scheduler import manage_trades
from src.entry_points.scheduler.get_fundamental_data import process_data
from src.entry_points.scheduler.scheduler import (
    get_fundamental_trend_data,
    process_fundamental_events,
)
from src.entry_points.scheduler.manage_trades import manage_trades_handler
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
    async def get(self):
        """Deletes the database"""
        logger.info("Get system info")
        return {
            "time": datetime.now(tz=get_localzone()),
            "system": "ok",
            "version": "1.1.1 - implement half spread cost",
        }

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
            close = data.iloc[-1]["close"]
            stop = data.iloc[-1]["low"]

            event = OpenTradeEvent(
                forex_pair=ForexPairEnum.AUDUSD,
                sentiment=SentimentEnum.BULLISH,
                stop=0.63181,
                close=float(close),
                limit=None,
            )

            is_buy, _, _, _, _ = await get_trade_parameters(
                event, self.uow, ForexPairEnum.AUDUSD.value.split("_")
            )

            return await self.uow.fxcm_connection.open_trade(
                instrument=ForexPairEnum.AUDUSD,
                is_buy=is_buy,
                amount=int(20),
                stop=event.stop,
                limit=None,
            )
        if debug_task == DebugEnum.TestModifyTrade:
            return await self.uow.fxcm_connection.modify_trade(
                trade_id="511", stop=1.07944
            )
        if debug_task == DebugEnum.GetTradeState:
            try:
                (
                    state,
                    realised_pl,
                ) = await self.uow.fxcm_connection.get_trade_state(
                    trade_id=18140
                )
                if state != "OPEN":
                    pass
                    # trade.position = PositionEnum.CLOSED
                    # trade.realised_pl = realised_pl
                    # trade.is_winner = True if realised_pl > 0 else False
                    # await self.uow.trade_repository.save(trade)
            except Exception as e:
                logger.error(e)

        if debug_task == DebugEnum.TestCloseTrade:
            try:
                return await self.uow.fxcm_connection.close_trade("18152", 20)
            except Exception as e:
                pass

        if debug_task == DebugEnum.TestGetTrades:
            async with self.uow:
                trades = await self.uow.trade_repository.get_open_trades()
                return await self.uow.fxcm_connection.get_open_positions()

        if debug_task == DebugEnum.TestManageTrade:
            return await manage_trades_handler()

        if debug_task == DebugEnum.TestProcessEvents:
            return await process_fundamental_events()

        if debug_task == DebugEnum.TestGetPendingOrders:
            return await self.uow.fxcm_connection.get_pending_orders()

        if debug_task == DebugEnum.TestCancelPendingOrder:
            orders = await self.uow.fxcm_connection.get_pending_orders()
            for order in orders:
                await self.uow.fxcm_connection.cancel_pending_order(order.id)

        if debug_task == DebugEnum.LoadData:
            for i in range(1, 120):
                if os.environ.get("DEPLOY_ENV", "local") == "aws":
                    date_ = datetime.now(
                        pytz.timezone("America/New_York")
                    ) - timedelta(days=i)
                else:
                    date_ = datetime.now(pytz.utc) - timedelta(days=i)
                if date_.weekday() < 5:
                    logger.info(f"Getting fundamental data for {date_}")
                    await process_data(date_=date_, load_data=True)

        if debug_task == DebugEnum.TestGetSpread:
            speard = await self.uow.fxcm_connection.get_spread(
                ForexPairEnum.USDCAD
            )
            return speard
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
