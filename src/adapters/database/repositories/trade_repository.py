import datetime
from typing import Iterator
from src.domain.trade import Trade

from src.adapters.database.repositories.base_repository import BaseRepository


class TradeRepository(BaseRepository):
    async def get_all(self) -> Iterator[Trade]:
        """Get all trade objects"""
        return Trade.objects()

    async def get_trade_by_trade_id(self, trade_id: str) -> Trade:
        """Get a single trade"""
        return Trade.objects(trade_id=trade_id).first()
