from fastapi_restful import set_responses, Resource
from src.adapters.database.sql.db_connect import Database
from src.adapters.database.sql.model import metadata_obj
from src.entry_points.scheduler.scheduler import get_fundamental_trend_data
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.container.container import Container


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
        await self.db.reset_db()
        return "done"

    @set_responses(str, 200)
    async def put(self):
        """Deletes the database"""
        await get_fundamental_trend_data()
        return "done"
