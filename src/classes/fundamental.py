from dataclasses import dataclass
from src.config import CurrencyEnum, SentimentEnum, CalendarEventEnum
from mongoengine import *


@dataclass
class FundamentalData(Document):
    def __init__(
        self,
        currency,
        last_updated,
        forecast,
        actual,
        previous,
        calendar_event,
        sentiment,
        *args,
        **values
    ):
        super().__init__(*args, **values)
        self.currency = currency
        self.last_updated = last_updated
        self.calendar_event = calendar_event
        self.forecast = forecast
        self.actual = actual
        self.previous = previous
        self.sentiment = sentiment
        self._id = {"currency": currency.value, "last_updated": last_updated}

    currency = EnumField(CurrencyEnum)
    last_updated = DateTimeField()
    calendar_event = EnumField(CalendarEventEnum)
    forecast = FloatField()
    actual = FloatField()
    previous = FloatField()
    sentiment = EnumField(SentimentEnum)
    _id = DictField(primary_key=True)


@dataclass
class FundamentalTrend(Document):
    last_updated = DateTimeField()
    currency = StringField()
