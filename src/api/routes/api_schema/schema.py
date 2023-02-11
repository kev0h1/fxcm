from fastapi_camelcase import CamelModel
from datetime import datetime
from pydantic import Field
from src.config import SentimentEnum, CurrencyEnum, CalendarEventEnum


class Base(CamelModel):
    def dict(self, **kwargs):
        output = super().dict(**kwargs)
        for k, v in output.items():
            if isinstance(v, datetime):
                output[k] = v.isoformat()
        return output

    class Config:
        arbitraty_types_allowed = True


class FundamentalSchema(Base):
    currency: CurrencyEnum
    last_updated: datetime
    calendar_event: CalendarEventEnum
    forecast: float = Field(default=None)
    actual: float = Field(default=None)
    previous: float = Field(default=None)
    sentiment: SentimentEnum = Field(default=SentimentEnum.FLAT)
