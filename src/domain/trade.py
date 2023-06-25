from dataclasses import dataclass, field
from datetime import datetime
from src.config import (
    CurrencyEnum,
    PositionEnum,
    SignalTypeEnum,
    ForexPairEnum,
)
from decimal import Decimal


@dataclass
class Trade:
    trade_id: int
    position_size: int
    stop: Decimal
    limit: Decimal
    is_buy: bool
    signal: SignalTypeEnum
    base_currency: CurrencyEnum
    quote_currency: CurrencyEnum
    forex_currency_pair: ForexPairEnum
    is_winner: bool = field(default=None)
    initiated_date: datetime = field(default=datetime.now())
    position: PositionEnum = field(default=PositionEnum.OPEN)

    def __post_init__(self):
        currencies = self.forex_currency_pair.value.split("/")
        assert self.base_currency.value == currencies[0]
        assert self.quote_currency.value == currencies[1]


# bullish trades would be trades where you are buying the base currency or selling the quote currency

# bearish trades would be trades where you are selling the base currency or buying the quote currency
