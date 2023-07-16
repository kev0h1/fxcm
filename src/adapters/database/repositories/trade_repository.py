from src.config import CurrencyEnum, ForexPairEnum, PositionEnum
from src.domain.trade import Trade as TradeDomain
from src.adapters.database.mongo.trade_model import (
    Trade as TradeModel,
    map_to_db_model,
    map_to_domain_model,
)
from mongoengine import Q


class TradeRepository:
    async def save(self, obj: TradeDomain) -> None:
        """Add an object"""
        trade_model = await map_to_db_model(obj)
        trade_model.save()
        return await map_to_domain_model(trade_model)

    async def get_all(self) -> list[TradeDomain]:
        """Get all trade objects"""
        return [await map_to_domain_model(obj) for obj in TradeModel.objects()]

    async def get_trade_by_trade_id(self, trade_id: str) -> TradeDomain:
        """Get a single trade"""
        return await map_to_domain_model(
            TradeModel.objects(trade_id=trade_id).first()
        )

    async def get_bullish_trades(
        self, currency: CurrencyEnum
    ) -> list[TradeDomain]:
        """Get all bullish trades"""
        return [
            await map_to_domain_model(obj)
            for obj in TradeModel.objects(
                (
                    Q(is_buy=True) & Q(base_currency=currency)
                    | Q(is_buy=False) & Q(quote_currency=currency)
                )
                & Q(position=PositionEnum.OPEN)
            )
        ]

    async def get_bearish_trades(
        self, currency: CurrencyEnum
    ) -> list[TradeDomain]:
        """Get all bearish trades"""
        return [
            await map_to_domain_model(obj)
            for obj in TradeModel.objects(
                (
                    Q(is_buy=False) & Q(base_currency=currency)
                    | Q(is_buy=True) & Q(quote_currency=currency)
                )
                & Q(position=PositionEnum.OPEN)
            )
        ]

    async def get_open_trades_by_forex_pair(
        self, forex_pair: ForexPairEnum, is_buy: bool
    ) -> list[TradeDomain]:
        """Get all open trades by forex pair"""
        return [
            await map_to_domain_model(obj)
            for obj in TradeModel.objects(
                forex_currency_pair=forex_pair,
                position=PositionEnum.OPEN,
                is_buy=is_buy,
            )
        ]
