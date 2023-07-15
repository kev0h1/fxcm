from datetime import date, datetime
from typing import Tuple, Union
from src.config import CurrencyEnum, SentimentEnum

from src.domain.fundamental import CalendarEvent, FundamentalData
from src.service_layer.uow import MongoUnitOfWork
from bs4 import element


class BaseScraper:
    async def set_scraper_params(
        self, date_: datetime = datetime.today()
    ) -> None:
        raise NotImplementedError

    async def make_request(self) -> None:
        raise NotImplementedError

    async def get_scraped_calendar_items(
        self, uow: MongoUnitOfWork
    ) -> list[Tuple[CalendarEvent, CurrencyEnum, datetime]]:
        raise NotImplementedError

    @staticmethod
    async def get_correct_date_format(
        date_: datetime = datetime.today(),
    ) -> str:
        """Get the correct day format"""
        raise NotImplementedError

    @staticmethod
    async def get_url_for_today(date_: datetime) -> str:
        """Get the url to search for today"""

        raise NotImplementedError

    async def __get_calendar_objects(self) -> element.ResultSet:
        """Get all calendar objects"""

    async def __filter_expand_objects(
        self, calendar_objects: element.ResultSet
    ) -> list:
        """Filter all expand objects
        This follows get calendar objects
        """
        raise NotImplementedError

    async def __group_list_by_date(self, data: list) -> list:
        """Groups the data by date
        This follows filtering of the unwanted data
        """
        raise NotImplementedError

    async def get_fundamental_items(self) -> list:
        """Return fundamental data to iterate"""
        raise NotImplementedError

    async def get_impact(self, element: element.Tag) -> str:
        """Get the impact of the news"""
        raise NotImplementedError

    async def get_impact_value(self, impact) -> str:  # type: ignore
        """Returns impact value"""
        raise NotImplementedError

    async def get_event_values(
        self, element: element.Tag, class_name: str
    ) -> Union[str, None]:
        """Get event values"""
        raise NotImplementedError

    async def get_actual_value(
        self, element: element.Tag, class_name: str
    ) -> Tuple[str, SentimentEnum]:
        """Get actual values and sentiment"""
        raise NotImplementedError

    async def get_strength(self, data) -> SentimentEnum:  # type: ignore
        """Get strength"""
        raise NotImplementedError

    async def get_time_value(
        self, grouped_data: list[element.Tag], day_index: int, tag_index: int
    ) -> Union[None, datetime.time]:  # type: ignore
        """Get the time value for an event"""
        raise NotImplementedError

    async def get_absolute_value(self, value: str) -> Union[float, None]:
        """Get the absolute value of percentage value"""

    async def get_date_value(self, value: str) -> date:
        """Return the current date"""
        raise NotImplementedError

    async def create_fundamental_object(
        self, tag: element.Tag, date_time: datetime
    ) -> FundamentalData:
        """create fundamental object"""
        raise NotImplementedError

    async def create_calendar_event(
        self,
        tag: element.Tag,
    ) -> Union[None, CalendarEvent]:
        """Create calendar object"""
        raise NotImplementedError
