import datetime
from typing import Union
from src.config import SentimentEnum

from src.domain.fundamental import CalendarEvent


class BaseScraper:
    async def get_fundamental_items(self):
        """Return fundamental data to iterate"""

    @staticmethod
    async def get_url_for_today(date_: datetime = datetime.datetime.today()):
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
