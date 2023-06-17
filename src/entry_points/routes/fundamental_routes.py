from datetime import date
from typing import List
from fastapi_restful import set_responses, Resource
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.domain.fundamental import FundamentalData
from src.config import CurrencyEnum
from src.adapters.database.mongo.mongo_connect import Database
from src.service_layer.fundamental_service import FundamentalDataService
from src.container.container import Container
from src.entry_points.routes.api_schema.schema import FundamentalSchema


class FundamentalResource(Resource):
    @inject
    def __init__(
        self,
        fundamental_data_service: FundamentalDataService = Depends(
            Provide[Container.fundamental_data_service],
        ),
        db: Database = Depends(Provide[Container.db]),
    ) -> None:
        super().__init__()
        self.service = fundamental_data_service
        self._db = db

    @set_responses(List[FundamentalSchema], 200)
    async def get(self, date: date = None, currency: CurrencyEnum = None):
        """Deletes the database"""
        api_data = []
        kwargs = {}
        if currency:
            kwargs["currency"] = currency
        if date:
            kwargs["last_updated"] = date
        with self._db.get_session():
            data: List[
                FundamentalData
            ] = self.service.get_all_fundamental_data(**kwargs)
            for value in data:
                api_data.append(FundamentalSchema(**value.to_mongo()))
            return api_data
