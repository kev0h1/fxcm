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
from src.service_layer.uow import MongoUnitOfWork


class FundamentalResource(Resource):
    @inject
    def __init__(
        self,
        fundamental_data_service: FundamentalDataService = Depends(
            Provide[Container.fundamental_data_service],
        ),
        uow: MongoUnitOfWork = Depends(Provide[Container.uow]),
    ) -> None:
        super().__init__()
        self.service = fundamental_data_service
        self._uow = uow

    @set_responses(List[FundamentalSchema], 200)
    async def get(self, date: date = None, currency: CurrencyEnum = None):
        """Deletes the database"""
        api_data = []
        kwargs = {}
        if currency:
            kwargs["currency"] = currency
        if date:
            kwargs["last_updated"] = date
        async with self._uow:
            data: List[
                FundamentalData
            ] = await self.service.get_all_fundamental_data(**kwargs)
            for value in data:
                api_data.append(FundamentalSchema(**value.to_mongo()))
            return api_data
