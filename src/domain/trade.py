from dataclasses import dataclass, field
from datetime import datetime
from src.config import (
    CurrencyEnum,
    PositionEnum,
    ForexPairEnum,
)


@dataclass
class Trade:
    trade_id: str
    units: float
    close: float
    stop: float
    limit: float
    is_buy: bool
    base_currency: CurrencyEnum
    quote_currency: CurrencyEnum
    forex_currency_pair: ForexPairEnum
    half_spread_cost: float
    new_close: float = field(default=None)
    realised_pl: float = field(default=None)
    is_winner: bool = field(default=False)
    initiated_date: datetime = field(default=datetime.now())
    position: PositionEnum = field(default=PositionEnum.OPEN)
    sl_pips: float = field(default=None)

    def __post_init__(self) -> None:
        currencies = self.forex_currency_pair.value.split("/")
        assert self.base_currency.value == currencies[0]
        assert self.quote_currency.value == currencies[1]


# bullish trades would be trades where you are buying the base currency or selling the quote currency

# bearish trades would be trades where you are selling the base currency or buying the quote currency
