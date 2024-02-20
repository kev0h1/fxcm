from __future__ import annotations
from datetime import datetime
from typing import Iterator
from src.domain.trade import Trade
from src.config import CurrencyEnum, SentimentEnum
from typing import Iterator


from src.service_layer.uow import MongoUnitOfWork


class TradeService:
    def __init__(self, uow: MongoUnitOfWork) -> None:
        self._uow: MongoUnitOfWork = uow

    async def get_all_trade_data(self, **kwargs) -> Iterator[Trade]:
        """Get the trade data"""
        return await self._uow.trade_repository.get_all(**kwargs)

    async def get_sum_of_realised_pl(self) -> Iterator[Trade]:
        """Get the trade data"""
        return await self._uow.trade_repository.get_sum_of_realised_pl()
