from datetime import datetime
from typing import Union
from src.config import (
    CurrencyEnum,
    ForexPairEnum,
    PositionEnum,
)
from src.domain.trade import Trade as TradeDomain
from mongoengine import (
    FloatField,
    BooleanField,
    DateTimeField,
    EnumField,
    Document,
    StringField,
)


class Trade(Document):
    def __init__(
        self,
        trade_id: int,
        units: float,
        stop: float,
        is_buy: bool,
        base_currency: CurrencyEnum,
        quote_currency: CurrencyEnum,
        forex_currency_pair: ForexPairEnum,
        is_winner: bool,
        initiated_date: datetime,
        position: PositionEnum,
        close: float,
        half_spread_cost: float,
        limit: float = None,
        realised_pl: float = None,
        sl_pips: float = None,
        *args,
        **values
    ) -> None:
        super().__init__(*args, **values)
        self.trade_id = trade_id
        self.units = units
        self.stop = stop
        self.limit = limit
        self.is_buy = is_buy
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        self.forex_currency_pair = forex_currency_pair
        self.is_winner = is_winner
        self.initiated_date = initiated_date
        self.position = position
        self.close = close
        self.realised_pl = realised_pl
        self.sl_pips = sl_pips
        self.half_spread_cost = half_spread_cost

    trade_id = StringField(primary_key=True)
    units = FloatField()
    stop = FloatField()
    close = FloatField()
    new_close = FloatField()
    realised_pl = FloatField()
    sl_pips = FloatField()
    limit = FloatField(allow_none=True)
    is_buy = BooleanField()
    is_winner = BooleanField()
    initiated_date = DateTimeField()
    base_currency = EnumField(CurrencyEnum)
    quote_currency = EnumField(CurrencyEnum)
    forex_currency_pair = EnumField(ForexPairEnum)
    position = EnumField(PositionEnum)
    half_spread_cost = FloatField()


def map_to_db_model(trade: TradeDomain) -> Union[Trade, None]:
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
        units=trade.units,
        stop=trade.stop,
        limit=trade.limit,
        is_buy=trade.is_buy,
        base_currency=trade.base_currency,
        quote_currency=trade.quote_currency,
        forex_currency_pair=trade.forex_currency_pair,
        is_winner=trade.is_winner,
        initiated_date=trade.initiated_date,
        position=trade.position,
        close=trade.close,
        new_close=trade.new_close,
        realised_pl=trade.realised_pl,
        sl_pips=trade.sl_pips,
        half_spread_cost=trade.half_spread_cost,
    )


def map_to_domain_model(trade: Trade) -> Union[TradeDomain, None]:
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
        units=trade.units,
        stop=trade.stop,
        limit=trade.limit,
        is_buy=trade.is_buy,
        base_currency=trade.base_currency,
        quote_currency=trade.quote_currency,
        forex_currency_pair=trade.forex_currency_pair,
        is_winner=trade.is_winner,
        initiated_date=trade.initiated_date,
        position=trade.position,
        close=trade.close,
        new_close=trade.new_close,
        realised_pl=trade.realised_pl,
        sl_pips=trade.sl_pips,
        half_spread_cost=trade.half_spread_cost,
    )
