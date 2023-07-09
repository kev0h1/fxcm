from fastapi_restful import set_responses, Resource
from src.adapters.database.mongo.mongo_connect import Database
from src.config import CurrencyEnum, SentimentEnum
from src.domain.events import CloseTradeEvent
from src.entry_points.scheduler.scheduler import get_fundamental_trend_data
from src.entry_points.scheduler.get_technical_signal import (
    get_technical_signal,
)
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.container.container import Container
from src.logger import get_logger
from src.service_layer.uow import MongoUnitOfWork
from fastapi import FastAPI, BackgroundTasks
from src.config import DebugEnum

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

    @set_responses(str, 200)
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
