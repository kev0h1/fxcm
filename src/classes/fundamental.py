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

    @classmethod
    def get_all_fundamental_data(cls, session: Session, **kwargs):
        """Get trades"""
        return session.query(cls).filter_by(**kwargs).all()


@dataclass
class FundamentalTrend:
    last_updated: datetime
    currency: CurrencyEnum
    sentiment: SentimentEnum = field(default=SentimentEnum.FLAT)

    @classmethod
    def get_trend_data(cls, session: Session, **kwargs):
        """Get trades"""
        return session.query(cls).filter_by(**kwargs).all()
