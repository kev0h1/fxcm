import pytz
from tzlocal import get_localzone
from src.config import CurrencyEnum, SentimentEnum
from mongoengine import *
from datetime import datetime, timezone
from src.domain.fundamental import (
    FundamentalData as FundamentalDataDomain,
    CalendarEvent as CalendarEventDomain,
)


class CalendarEvent(EmbeddedDocument):
    def __init__(
        self,
        calendar_event: str,
        sentiment: SentimentEnum,
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
        self,
        currency: CurrencyEnum,
        last_updated: datetime,
        aggregate_sentiment: SentimentEnum,
        processed: bool,
        calendar_events: list[CalendarEvent] = None,
        *args,
        **values
    ):
        super().__init__(*args, **values)
        self.currency = currency
        self.last_updated = last_updated
        self._id = {"currency": currency.value, "last_updated": last_updated}
        self.aggregate_sentiment = aggregate_sentiment
        self.processed = processed
        self.calendar_events = calendar_events

    calendar_events = EmbeddedDocumentListField(CalendarEvent)
    currency = EnumField(CurrencyEnum)
    last_updated = DateTimeField()
    aggregate_sentiment = EnumField(SentimentEnum)
    _id = DictField(primary_key=True)
    processed = BooleanField()


async def map_to_db_model(fundamental_data: FundamentalDataDomain):
    """Maps fundamental data domain model to database model

    Args:
        fundamental_data (FundamentalDataDomain): _description_

    Returns:
        _type_: _description_
    """
    if not fundamental_data:
        return None

    calendar_events = [
        CalendarEvent(
            calendar_event=calendar_event.calendar_event,
            sentiment=calendar_event.sentiment,
            forecast=calendar_event.forecast,
            actual=calendar_event.actual,
            previous=calendar_event.previous,
        )
        for calendar_event in fundamental_data.calendar_events
    ]
    return FundamentalData(
        currency=fundamental_data.currency,
        last_updated=fundamental_data.last_updated,
        aggregate_sentiment=fundamental_data.aggregate_sentiment,
        calendar_events=calendar_events,
        processed=fundamental_data.processed,
    )


async def map_to_domain_model(fundamental_data: FundamentalData):
    """Map from database model to domain model

    Args:
        fundamental_data (FundamentalData): _description_
    """
    if not fundamental_data:
        return None

    timezone = pytz.timezone("UTC")
    calendar_events = [
        CalendarEventDomain(
            calendar_event=calendar_event.calendar_event,
            sentiment=calendar_event.sentiment,
            forecast=calendar_event.forecast,
            actual=calendar_event.actual,
            previous=calendar_event.previous,
        )
        for calendar_event in fundamental_data.calendar_events
    ]
    return FundamentalDataDomain(
        currency=fundamental_data.currency,
        last_updated=timezone.localize(fundamental_data.last_updated),
        aggregate_sentiment=fundamental_data.aggregate_sentiment,
        calendar_events=calendar_events,
        processed=fundamental_data.processed,
    )
