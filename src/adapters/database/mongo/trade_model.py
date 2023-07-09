from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Union
from src.config import (
    CurrencyEnum,
    ForexPairEnum,
    SignalTypeEnum,
    PositionEnum,
)
from src.domain.trade import Trade as TradeDomain
from mongoengine import (
    FloatField,
    IntField,
    BooleanField,
    DateTimeField,
    EnumField,
    Document,
)


class Trade(Document):
    def __init__(
        self,
        trade_id: int,
        position_size: int,
        stop: Decimal,
        limit: Decimal,
        is_buy: bool,
        signal: SignalTypeEnum,
        base_currency: CurrencyEnum,
        quote_currency: CurrencyEnum,
        forex_currency_pair: ForexPairEnum,
        position: PositionEnum,
        *args,
        **values
    ) -> None:
        super().__init__(*args, **values)
        self.trade_id = trade_id
        self.position_size = position_size
        self.stop = stop
        self.limit = limit
        self.is_buy = is_buy
        self.signal = signal
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.forex_currency_pair = forex_currency_pair
        self.position = position

    trade_id = IntField(primary_key=True)
    position_size = IntField()
    stop = FloatField()
    limit = FloatField()
    is_buy = BooleanField()
    signal = EnumField(SignalTypeEnum)
    is_winner = BooleanField(default=False)
    initiated_date = DateTimeField(default=datetime.now())
    base_currency = EnumField(CurrencyEnum)
    quote_currency = EnumField(CurrencyEnum)
    forex_currency_pair = EnumField(ForexPairEnum)
    position = EnumField(PositionEnum)


async def map_to_db_model(trade: TradeDomain) -> Union[Trade, None]:
    """Maps trade domain model to database model

    Args:
        trade (Trade): trade domain model

    Returns:
        Trade: database model
    """
    if not trade:
        return None
    return Trade(
        trade_id=trade.trade_id,
        position_size=trade.position_size,
        stop=trade.stop,
        limit=trade.limit,
        is_buy=trade.is_buy,
        signal=trade.signal,
        base_currency=trade.base_currency,
        quote_currency=trade.quote_currency,
        forex_currency_pair=trade.forex_currency_pair,
        position=trade.position,
    )


async def map_to_domain_model(trade: Trade) -> Union[TradeDomain, None]:
    """Maps trade database model to domain model

    Args:
        trade (Trade): trade database model

    Returns:
        Trade: domain model
    """
    if not trade:
        return None
    return TradeDomain(
        trade_id=trade.trade_id,
        position_size=trade.position_size,
        stop=trade.stop,
        limit=trade.limit,
        is_buy=trade.is_buy,
        signal=trade.signal,
        is_winner=trade.is_winner,
        position=trade.position,
        initiated_date=trade.initiated_date,
        base_currency=trade.base_currency,
        quote_currency=trade.quote_currency,
        forex_currency_pair=trade.forex_currency_pair,
    )
