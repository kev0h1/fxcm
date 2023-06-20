from typing import Iterator
from src.config import CurrencyEnum
from src.domain.trade import Trade as TradeDomain
from src.adapters.database.mongo.trade_model import (
    Trade as TradeModel,
    map_to_db_model,
    map_to_domain_model,
)
from mongoengine import Q


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

    async def get_bullish_trades(
        self, currency: CurrencyEnum
    ) -> Iterator[TradeDomain]:
        """Get all bullish trades"""
        return [
            map_to_domain_model(obj)
            for obj in TradeModel.objects(
                Q(is_buy=True) & Q(base_currency=currency)
                | Q(is_buy=False) & Q(quote_currency=currency)
            )
        ]

    async def get_bearish_trades(
        self, currency: CurrencyEnum
    ) -> Iterator[TradeDomain]:
        """Get all bearish trades"""
        return [
            map_to_domain_model(obj)
            for obj in TradeModel.objects(
                Q(is_buy=False) & Q(base_currency=currency)
                | Q(is_buy=True) & Q(quote_currency=currency)
            )
        ]
