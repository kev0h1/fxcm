from datetime import date
from typing import Any, List
from fastapi_restful import set_responses, Resource
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.domain.trade import Trade
from src.container.container import Container
from src.entry_points.routes.api_schema.schema import TradeSchema
from src.service_layer.trade_service import TradeService
from src.service_layer.uow import MongoUnitOfWork
from src.logger import get_logger

logger = get_logger(__name__)


class TradeResource(Resource):
    @inject
    def __init__(
        self,
        trade_service: TradeService = Depends(
            Provide[Container.trade_service],
        ),
        uow: MongoUnitOfWork = Depends(Provide[Container.uow]),
    ) -> None:
        super().__init__()
        self.service = trade_service
        self._uow = uow

    @set_responses(List[TradeSchema], 200)
    async def get(self, date: date = None):
        """Deletes the database"""
        kwargs = {}
        if date:
            kwargs["last_updated"] = date
        async with self._uow:
            logger.info(f"Getting fundamental data with kwargs: {kwargs}")
            data: List[Trade] = await self.service.get_all_trade_data(**kwargs)
            return data
