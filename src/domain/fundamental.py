from dataclasses import dataclass, field
from src.config import CurrencyEnum, SentimentEnum
from mongoengine import *
from datetime import datetime
from decimal import Decimal


@dataclass
class CalendarEvent:
    calendar_event: str
    sentiment: SentimentEnum
    forecast: Decimal = field(default=None)
    actual: Decimal = field(default=None)
    previous: Decimal = field(default=None)


@dataclass
class FundamentalData:
    currency: CurrencyEnum
    last_updated: datetime
    processed: bool = field(default=False)
    aggregate_sentiment: SentimentEnum = field(default=SentimentEnum.FLAT)
    calendar_events: list[CalendarEvent] = field(default_factory=list)
