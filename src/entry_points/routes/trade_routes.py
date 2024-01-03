from datetime import date
from typing import Any, List
from fastapi_restful import set_responses, Resource
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.domain.trade import Trade
from src.container.container import Container
from src.service_layer.trade_service import TradeService
from src.entry_points.routes.api_schema.schema import (
    TradeSchema,
    TradeStatistic,
)
from src.service_layer.uow import MongoUnitOfWork
from src.logger import get_logger
from src.config import PositionEnum

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

    @set_responses(TradeStatistic, 200)
    async def get(self, date: date = None):
        """Deletes the database"""
        kwargs = {}
        if date:
            kwargs["last_updated"] = date
        async with self._uow:
            logger.info(f"Getting fundamental data with kwargs: {kwargs}")
            data: List[Trade] = await self.service.get_all_trade_data(**kwargs)
            pnl = 0
            num_winners = 0
            num_losers = 0
            for trade in data:
                if trade.realised_pl is not None:
                    pnl += trade.realised_pl

                if trade.is_winner:
                    num_winners += 1
                elif trade.position == PositionEnum.CLOSED:
                    num_losers += 1

            number_of_trades = len(data)
            trade_schemas = [TradeSchema(**vars(trade)) for trade in data]
            trade_statistics = {
                "pnl": pnl,
                "number_of_winners": num_winners,
                "number_of_losers": num_losers,
                "number_of_trades": number_of_trades,
                "trades": trade_schemas,
            }

            return TradeStatistic(**trade_statistics)


class TradePl(Resource):
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

    @set_responses(Any, 200)
    async def get(self):
        """Deletes the database"""

        async with self._uow:
            logger.info(f"")
            data: float = await self.service.get_sum_of_realised_pl()
            return data
