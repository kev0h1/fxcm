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
    currency: CurrencyEnum


@dataclass
class TechnicalEvent(Event):
    currency: CurrencyEnum
