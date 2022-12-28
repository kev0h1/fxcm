from dataclasses import dataclass
from src.config import CurrencyEnum, SentimentEnum, CalendarEventEnum
from datetime import datetime


@dataclass
class FundamentalData:
    currency: CurrencyEnum
    last_updated: datetime
    forecast: float
    actual: float
    previous: float
    calendar_event: CalendarEventEnum
    
    


@dataclass
class FundamentalTrend:
    sentiment: SentimentEnum
    fundamental_data: FundamentalData
