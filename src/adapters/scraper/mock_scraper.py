import itertools
from typing import Tuple, Union
from bs4 import element
import pytz
from src.adapters.scraper.base_scraper import BaseScraper
from src.domain.fundamental import CalendarEvent, FundamentalData
from datetime import datetime, date
from src.config import (
    CurrencyEnum,
    SentimentEnum,
)
from src.service_layer.uow import MongoUnitOfWork


class MockScraper(BaseScraper):
    def __init__(self, sentiment, is_processed: bool = False):
        self.sentiment = sentiment
        self.is_processed = is_processed

    async def set_scraper_params(
        self,
        date_: datetime = datetime.today(),
    ) -> None:
        self.date_ = date_
        self.url = await self.get_url_for_today(date_=self.date_)

    async def make_request(self) -> None:
        ...

    async def get_scraped_calendar_items(
        self, uow: MongoUnitOfWork
    ) -> list[Tuple[CalendarEvent, CurrencyEnum, datetime]]:
        date_ = datetime.now(tz=pytz.utc)
        calendar_event = CalendarEvent(
            calendar_event="mock_event",
            sentiment=self.sentiment,
            forecast=1.2,
            actual=1.3,
            previous=1.1,
        )
        fundamental_data = FundamentalData(
            currency=CurrencyEnum.USD,
            last_updated=date_,
            calendar_events=[calendar_event],
            processed=self.is_processed,
        )

        await uow.fundamental_data_repository.save(fundamental_data)
        return [(calendar_event, CurrencyEnum.USD, date_)]

    @staticmethod
    async def get_correct_date_format(
        date_: datetime = datetime.today(),
    ) -> str:
        """Get the correct day format"""
        return date_.strftime("%b%d.%Y")

    @staticmethod
    async def get_url_for_today(date_: datetime) -> str:
        """Get the url to search for today"""

        return "127.0.0.1"

    async def __get_calendar_objects(self) -> element.ResultSet:
        """Get all calendar objects"""

    async def __filter_expand_objects(
        self, calendar_objects: element.ResultSet
    ) -> list:
        """Filter all expand objects
        This follows get calendar objects
        """

    async def __group_list_by_date(self, data: list) -> list:
        """Groups the data by date
        This follows filtering of the unwanted data
        """

    async def get_fundamental_items(self) -> list:
        """Return fundamental data to iterate"""

    async def get_impact(self, element: element.Tag) -> str:
        """Get the impact of the news"""

    async def get_impact_value(self, impact) -> str:  # type: ignore
        """Returns impact value"""

    async def get_event_values(
        self, element: element.Tag, class_name: str
    ) -> Union[str, None]:
        """Get event values"""

    async def get_actual_value(
        self, element: element.Tag, class_name: str
    ) -> Tuple[str, SentimentEnum]:
        """Get actual values and sentiment"""

    async def get_strength(self, data) -> SentimentEnum:  # type: ignore
        """Get strength"""

    async def get_time_value(
        self, grouped_data: list[element.Tag], day_index: int, tag_index: int
    ) -> Union[None, datetime.time]:  # type: ignore
        """Get the time value for an event"""

    async def get_absolute_value(self, value: str) -> Union[float, None]:
        """Get the absolute value of percentage value"""

    async def get_date_value(self, value: str) -> date:
        """Return the current date"""
        date = datetime.strptime(value, "%a%b %d").date()
        return datetime(datetime.today().year, date.month, date.day)

    async def create_fundamental_object(
        self, tag: element.Tag, date_time: datetime
    ) -> FundamentalData:
        """create fundamental object"""

    async def create_calendar_event(
        self,
        tag: element.Tag,
    ) -> Union[None, CalendarEvent]:
        """Create calendar object"""
