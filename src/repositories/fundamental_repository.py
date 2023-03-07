import datetime
from typing import Iterator
from src.classes.fundamental import FundamentalData
from src.config import CurrencyEnum, CalendarEventEnum
from src.repositories.base_repository import BaseRepository


class FundamentalDataRepository(BaseRepository):
    def get_all(self) -> Iterator[FundamentalData]:
        return FundamentalData.objects()

    def get_calendar_event(
        self,
        fundamental_data: FundamentalData,
        calendar_event: CalendarEventEnum,
    ):
        return fundamental_data.calendar_events.filter(
            calendar_event=calendar_event
        ).first()

    def get_fundamental_data(
        self, currency: CurrencyEnum, last_updated: datetime
    ) -> FundamentalData:
        return FundamentalData.objects(
            currency=currency, last_updated=last_updated
        ).first()
