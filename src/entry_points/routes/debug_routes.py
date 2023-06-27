from fastapi_restful import set_responses, Resource
from src.adapters.database.mongo.mongo_connect import Database
from src.entry_points.scheduler.scheduler import get_fundamental_trend_data
from src.entry_points.scheduler.get_technical_signal import (
    get_technical_signal,
)
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.container.container import Container
from src.logger import get_logger

logger = get_logger(__name__)


class DebugResource(Resource):
    @inject
    def __init__(
        self,
        db: Database = Depends(Provide[Container.db]),
    ) -> None:
        super().__init__()
        self.db = db

    @set_responses(str, 200)
    async def delete(self):
        """Deletes the database"""
        logger.info("Deleting database")
        await self.db.reset_db()
        return "done"

    @set_responses(str, 200)
    async def put(self):
        """Deletes the database"""
        logger.info("Manually retrieve fundamental data")
        await get_technical_signal()
        return "done"
