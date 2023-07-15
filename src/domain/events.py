from decimal import Decimal
from src.config import CurrencyEnum, ForexPairEnum, SentimentEnum
from dataclasses import dataclass


@dataclass
class Event:
    ...


@dataclass
class FundamentalEvent(Event):
    currency: CurrencyEnum


@dataclass
class CloseTradeEvent(Event):
    currency: CurrencyEnum
    sentiment: SentimentEnum


@dataclass
class CloseForexPairEvent(Event):
    forex_pair: ForexPairEnum
    sentiment: SentimentEnum


@dataclass
class OpenTradeEvent(Event):
    forex_pair: ForexPairEnum
    sentiment: SentimentEnum


@dataclass
class CreateTradeEvent(Event):
    currency: CurrencyEnum
    forex_pair: ForexPairEnum
    trade_id: str
    postion_size: int
    stop: Decimal
    limit: Decimal
    is_buy: bool


@dataclass
class TechnicalEvent(Event):
    currency: CurrencyEnum
