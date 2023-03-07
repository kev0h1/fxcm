from dataclasses import dataclass
from src.config import CurrencyEnum, SentimentEnum
from mongoengine import *
from datetime import datetime


class CalendarEvent(EmbeddedDocument):
    def __init__(
        self,
        calendar_event: str,
        sentiment: SentimentEnum = SentimentEnum.FLAT,
        forecast: float = None,
        actual: float = None,
        previous: float = None,
        *args,
        **values
    ):
        super().__init__(*args, **values)
        self.calendar_event = calendar_event
        self.forecast = forecast
        self.actual = actual
        self.previous = previous
        self.sentiment = sentiment

    calendar_event = StringField(required=True)
    forecast = FloatField()
    actual = FloatField()
    previous = FloatField()
    sentiment = EnumField(SentimentEnum)


class FundamentalData(Document):
    def __init__(
        self, currency: CurrencyEnum, last_updated: datetime, *args, **values
    ):
        super().__init__(*args, **values)
        self.currency = currency
        self.last_updated = last_updated
        self._id = {"currency": currency.value, "last_updated": last_updated}

    calendar_events = EmbeddedDocumentListField(CalendarEvent)
    currency = EnumField(CurrencyEnum)
    last_updated = DateTimeField()
    _id = DictField(primary_key=True)


@dataclass
class FundamentalTrend(Document):
    last_updated = DateTimeField()
    currency = StringField()
