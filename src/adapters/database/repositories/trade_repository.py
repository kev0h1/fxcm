import datetime
from typing import Iterator
from src.domain.trade import Trade as TradeDomain
from src.adapters.database.mongo.trade_model import (
    Trade as TradeModel,
    map_to_db_model,
    map_to_domain_model,
)


class TradeRepository:
    async def save(self, obj: TradeDomain):
        """Add an object"""
        map_to_db_model(obj.save())
        return obj

    async def get_all(self) -> Iterator[TradeDomain]:
        """Get all trade objects"""
        return [map_to_domain_model(obj) for obj in TradeModel.objects()]

    async def get_trade_by_trade_id(self, trade_id: str) -> TradeDomain:
        """Get a single trade"""
        return map_to_domain_model(
            TradeModel.objects(trade_id=trade_id).first()
        )
