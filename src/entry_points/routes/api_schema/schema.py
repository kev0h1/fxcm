from typing import List
from fastapi_camelcase import CamelModel
from datetime import datetime
from pydantic import Field
from src.config import (
    ForexPairEnum,
    PositionEnum,
    SentimentEnum,
    CurrencyEnum,
    CalendarEventEnum,
)


class Base(CamelModel):
    def dict(self, **kwargs):
        output = super().dict(**kwargs)
        for k, v in output.items():
            if isinstance(v, datetime):
                output[k] = v.isoformat()
        return output

    class Config:
        arbitraty_types_allowed = True


class CalendarEventSchema(Base):
    calendar_event: str
    forecast: float = Field(default=None)
    actual: float = Field(default=None)
    previous: float = Field(default=None)
    sentiment: SentimentEnum


class FundamentalSchema(Base):
    currency: CurrencyEnum
    last_updated: datetime
    processed: bool
    aggregate_sentiment: SentimentEnum
    calendar_events: List[CalendarEventSchema]


class TradeSchema(Base):
    trade_id: str
    units: float
    close: float
    stop: float
    limit: float = Field(default=None)
    is_buy: bool
    base_currency: CurrencyEnum
    quote_currency: CurrencyEnum
    forex_currency_pair: ForexPairEnum
    new_close: float = Field(default=None)
    realised_pl: float = Field(default=None)
    half_spread_cost: float = Field(default=None)
    is_winner: bool = Field(default=False)
    sl_pips: float = Field(default=None)
    initiated_date: datetime
    position: PositionEnum


class TradeStatistic(Base):
    pnl: float = Field(default=None)
    number_of_winners: int = Field(default=None)
    number_of_losers: int = Field(default=None)
    number_of_trades: int = Field(default=None)
    trades: list[TradeSchema] = Field(default=None)
