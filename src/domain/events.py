from src.config import CurrencyEnum
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


@dataclass
class OpenTradeEvent(Event):
    currency: CurrencyEnum


@dataclass
class TechnicalEvent(Event):
    currency: CurrencyEnum
