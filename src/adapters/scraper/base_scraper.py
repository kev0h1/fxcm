import datetime
from typing import Tuple, Union
from src.config import CurrencyEnum, SentimentEnum

from src.domain.fundamental import CalendarEvent, FundamentalData
from src.service_layer.uow import MongoUnitOfWork


class BaseScraper:
    async def get_fundamental_items(self) -> list[FundamentalData]:
        """Return fundamental data to iterate"""
        return [
            FundamentalData(
                currency=CurrencyEnum.USD,
                last_updated=datetime.datetime.today(),
                calendar_events=[
                    CalendarEvent(
                        calendar_event="calendar_event",
                        sentiment=SentimentEnum.FLAT,
                        forecast=1.2,
                        actual=1.2,
                        previous=1.2,
                    )
                ],
            )
        ]

    @staticmethod
    async def get_url_for_today(
        date_: datetime.datetime = datetime.datetime.today(),
    ) -> str:
        """Get the url to search for today"""
        return "%s?day=%s" % ("127.0.0.1/", date_.strftime("%b%d.%Y"))

    async def create_calendar_event(self) -> Union[None, CalendarEvent]:
        """Create calendar object"""

        return CalendarEvent(
            forecast=None,
            actual=None,
            previous=None,
            calendar_event="calendar_event",
            sentiment=SentimentEnum.FLAT,
        )

    async def get_event_values(self) -> str:
        """Get event values"""
        return "calendar_event"

    async def set_scraper_params(
        self, date_: datetime.datetime = datetime.datetime.today()
    ) -> None:
        """Set scraper params"""

    async def make_request(self) -> None:
        """Make request"""

    async def get_scraped_calendar_items(
        self,
        uow: MongoUnitOfWork,
    ) -> list[Tuple[CalendarEvent, CurrencyEnum, datetime.datetime]]:
        """Get scraped calendar items"""
        calendar_event = CalendarEvent(
            calendar_event="calendar_event",
            sentiment=SentimentEnum.FLAT,
            forecast=1.2,
            actual=1.2,
            previous=1.2,
        )

        fundamental_data = FundamentalData(
            currency=CurrencyEnum.USD,
            last_updated=datetime.datetime.today(),
            calendar_events=[calendar_event],
        )

        await uow.fundamental_data_repository.save(fundamental_data)
        return [(calendar_event, CurrencyEnum.USD, datetime.datetime.today())]
