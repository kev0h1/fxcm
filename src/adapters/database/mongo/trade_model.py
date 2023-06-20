from dataclasses import dataclass
from datetime import datetime
from src.config import (
    CurrencyEnum,
    ForexPairEnum,
    SignalTypeEnum,
    PositionEnum,
)
from mongoengine import *
from src.domain.trade import Trade as TradeDomain


class Trade(Document):
    def __init__(
        self,
        trade_id,
        position_size,
        stop,
        limit,
        is_buy,
        signal,
        base_currency,
        quote_currency,
        forex_currency_pair,
        position,
        *args,
        **values
    ):
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


def map_to_db_model(trade: TradeDomain):
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
    )


def map_to_domain_model(trade: Trade):
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
        initiated_date=trade.initiated_date,
        base_currency=trade.base_currency,
        quote_currency=trade.quote_currency,
        forex_currency_pair=trade.forex_currency_pair,
    )
