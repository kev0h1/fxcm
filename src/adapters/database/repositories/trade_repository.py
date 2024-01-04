from src.config import CurrencyEnum, ForexPairEnum, PositionEnum
from src.domain.trade import Trade as TradeDomain
from src.adapters.database.mongo.trade_model import (
    Trade as TradeModel,
    map_to_db_model,
    map_to_domain_model,
)
from mongoengine import Q
from datetime import timedelta


class TradeRepository:
    async def save(self, obj: TradeDomain) -> None:
        """Add an object"""
        trade_model = map_to_db_model(obj)
        trade_model.save()
        return obj

    async def get_all(self, **kwargs) -> list[TradeDomain]:
        """Get all trade objects"""
        date = None
        if "last_updated" in kwargs:
            date = kwargs.pop("last_updated")
            next_day = date + timedelta(days=1)
        objs = TradeModel.objects()

        if date:
            objs = objs.filter(
                initiated_date__gte=date, initiated_date__lte=next_day
            )

        return [map_to_domain_model(obj) for obj in objs]

    async def get_trade_by_trade_id(self, trade_id: str) -> TradeDomain:
        """Get a single trade"""
        return map_to_domain_model(
            TradeModel.objects(trade_id=trade_id).first()
        )

    async def get_bullish_trades(
        self, currency: CurrencyEnum
    ) -> list[TradeDomain]:
        """Get all bullish trades"""
        trades = TradeModel.objects(
            (
                Q(is_buy=True) & Q(base_currency=currency)
                | Q(is_buy=False) & Q(quote_currency=currency)
            )
            & Q(position=PositionEnum.OPEN)
        )
        return [map_to_domain_model(obj) for obj in trades]

    async def get_bearish_trades(
        self, currency: CurrencyEnum
    ) -> list[TradeDomain]:
        """Get all bearish trades"""
        trades = TradeModel.objects(
            (
                Q(is_buy=False) & Q(base_currency=currency)
                | Q(is_buy=True) & Q(quote_currency=currency)
            )
            & Q(position=PositionEnum.OPEN)
        )
        return [map_to_domain_model(obj) for obj in trades]

    async def get_open_trades_by_forex_pair_for_buy_or_sell(
        self, forex_pair: ForexPairEnum, is_buy: bool
    ) -> list[TradeDomain]:
        """Get all open trades by forex pair"""
        trades = TradeModel.objects(
            forex_currency_pair=forex_pair,
            position=PositionEnum.OPEN,
            is_buy=is_buy,
        )
        return [map_to_domain_model(obj) for obj in trades]

    async def get_open_trades_by_forex_pair(
        self, forex_pair: ForexPairEnum
    ) -> list[TradeDomain]:
        """Get all open trades by forex pair"""
        trades = TradeModel.objects(
            forex_currency_pair=forex_pair, position=PositionEnum.OPEN
        )
        return [map_to_domain_model(obj) for obj in trades]

    async def get_open_trades(self) -> list[TradeDomain]:
        """Get all open trades"""
        trades = TradeModel.objects(
            Q(position=PositionEnum.OPEN) | Q(realised_pl=None)
        )
        return [map_to_domain_model(obj) for obj in trades]

    async def get_distinct_forex_pairs(self) -> list[ForexPairEnum]:
        """Get all distinct forex pairs"""
        trades = TradeModel.objects().distinct("forex_currency_pair")
        return [ForexPairEnum(obj) for obj in trades]

    async def get_sum_of_realised_pl(self) -> float:
        """Get sum of realised pl"""
        return TradeModel.objects().sum("realised_pl")
