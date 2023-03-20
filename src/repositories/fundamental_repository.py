import datetime
from typing import Iterator
from src.classes.fundamental import FundamentalData
from src.config import CurrencyEnum, CalendarEventEnum
from src.repositories.base_repository import BaseRepository


class FundamentalDataRepository(BaseRepository):
    def get_all(self, **kwargs) -> Iterator[FundamentalData]:
        date = None
        if "last_updated" in kwargs:
            date = kwargs.pop("last_updated")
        objs = FundamentalData.objects(**kwargs)
        if date:
            return objs.filter(last_updated__gte=date)
        return objs

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

    def get_latest_fundamental_data(self, currency: CurrencyEnum):
        """Gets the latest fundamental data for a currency"""
        return (
            FundamentalData.objects(
                currency=currency,
            )
            .order_by("-last_updated")
            .first()
        )
