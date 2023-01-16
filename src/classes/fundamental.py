from dataclasses import dataclass, field
from src.config import CurrencyEnum, SentimentEnum, CalendarEventEnum
from datetime import datetime
from sqlalchemy.orm import Session


@dataclass
class FundamentalData:
    currency: CurrencyEnum
    last_updated: datetime
    calendar_event: CalendarEventEnum
    forecast: float = field(default=None)
    actual: float = field(default=None)
    previous: float = field(default=None)
    sentiment: SentimentEnum = field(default=SentimentEnum.FLAT)


@dataclass
class FundamentalTrend:
    last_updated: datetime
    currency: CurrencyEnum

    @classmethod
    def get_trend_data(cls, session: Session, **kwargs):
        """Get trades"""
        return session.query(cls).filter_by(**kwargs).all()

    @classmethod
    def get_trend_data_for_currency(
        cls, session: Session, currency: CurrencyEnum
    ):
        """Get trend data for currency"""
        return session.query(cls).filter_by(currency=currency).one_or_none()

    def update_sentiment(self):
        if self.fundamental_data:
            pass
