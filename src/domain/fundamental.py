from dataclasses import dataclass, field
from src.config import CurrencyEnum, SentimentEnum
from mongoengine import *
from datetime import datetime


@dataclass
class CalendarEvent:
    calendar_event: str
    sentiment: SentimentEnum
    forecast: float = field(default=None)
    actual: float = field(default=None)
    previous: float = field(default=None)


@dataclass
class FundamentalData:
    currency: CurrencyEnum
    last_updated: datetime
    processed: bool = field(default=False)
    aggregate_sentiment: SentimentEnum = field(default=SentimentEnum.FLAT)
    calendar_events: list[CalendarEvent] = field(default_factory=list)
