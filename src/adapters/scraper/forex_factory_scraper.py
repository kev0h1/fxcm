import itertools
from typing import Tuple, Union
from bs4 import BeautifulSoup, element
import pytz
from src.domain.fundamental import CalendarEvent, FundamentalData
import requests
from datetime import datetime, time, date
from src.config import (
    CurrencyEnum,
    ImpactEnum,
    SentimentEnum,
)
import re
from src.domain.errors.errors import (
    NoEconomicImpactDefined,
)
from pytz import timezone

from src.service_layer.uow import MongoUnitOfWork
from tzlocal import get_localzone

URL = "https://www.forexfactory.com/calendar"
CALENDAR_ACTUAL = "calendar__actual"
CALENDAR_FORECAST = "calendar__forecast"
CALENDAR_PREVIOUS = "calendar__previous"
CALENDAR_EVENT = "calendar__event"
CALENDAR_TIME = "calendar__time"
CALENDAR_DAY = "calendar__cell"
CALENDAR_CURRENCY = "calendar__currency"


class ForexFactoryScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0"
        }

    async def set_scraper_params(self, date_: datetime = datetime.today()):
        self.date_ = date_
        self.url = await self.get_url_for_today(date_=self.date_)

    async def make_request(self):
        page = requests.get(self.url, headers=self.headers, verify=False)
        self.soup = BeautifulSoup(page.content, "html.parser")

    async def get_scraped_calendar_items(
        self, uow: MongoUnitOfWork
    ) -> list[Tuple[CalendarEvent, CurrencyEnum, datetime]]:
        fundamental_items = await self.get_fundamental_items()
        scraped_data = fundamental_items[-1]
        scraped_items = []
        for index, data in enumerate(scraped_data):
            time = await self.get_time_value(fundamental_items, -1, index)
            if time is None:
                continue
            date_time = datetime.combine(self.date_, time)
            currency = await self.get_event_values(
                element=data, class_name=CALENDAR_CURRENCY
            )
            if currency not in CurrencyEnum.__members__:
                continue
            currency = CurrencyEnum(currency)
            scraped_calendar_event: CalendarEvent = (
                await self.create_calendar_event(tag=data)
            )
            if scraped_calendar_event:
                scraped_items.append(
                    (scraped_calendar_event, currency, date_time)
                )
                fundamental_data: FundamentalData = (
                    await uow.fundamental_data_repository.get_fundamental_data(
                        currency=currency, last_updated=date_time
                    )
                )
                if not fundamental_data:
                    fundamental_data: FundamentalData = (
                        await self.create_fundamental_object(
                            data, date_time=date_time
                        )
                    )
                    fundamental_data: FundamentalData = (
                        await uow.fundamental_data_repository.save(
                            fundamental_data
                        )
                    )
        return scraped_items

    @staticmethod
    async def get_correct_date_format(date_: datetime = datetime.today()):
        """Get the correct day format"""
        return date_.strftime("%b%d.%Y")

    @staticmethod
    async def get_url_for_today(date_: datetime):
        """Get the url to search for today"""
        today = await ForexFactoryScraper.get_correct_date_format(date_=date_)
        return "%s?day=%s" % (URL, today)

    async def __get_calendar_objects(self) -> element.ResultSet:
        """Get all calendar objects"""
        return self.soup.find_all("tr", {"class": "calendar__row"})

    async def __filter_expand_objects(
        self, calendar_objects: element.ResultSet
    ) -> list:
        """Filter all expand objects
        This follows get calendar objects
        """
        return [
            f
            for f in filter(
                lambda tr: "calendar__expand" not in tr["class"],
                calendar_objects,
            )
        ]

    async def __group_list_by_date(self, data: list) -> list:
        """Groups the data by date
        This follows filtering of the unwanted data
        """
        items = itertools.groupby(
            data, lambda tr: "calendar__row--day-breaker" in tr["class"]
        )

        return [list(i) for _, i in items]

    async def get_fundamental_items(self):
        """Return fundamental data to iterate"""
        objects = await self.__get_calendar_objects()
        filtered_objects = await self.__filter_expand_objects(objects)
        return await self.__group_list_by_date(filtered_objects)

    async def get_impact(self, element: element.Tag) -> str:
        """Get the impact of the news"""
        impact_values = ["low", "medium", "high"]
        impact = element.find("td", {"class": "calendar__impact"})
        if impact is None:
            raise NoEconomicImpactDefined("Cannot determine impact")
        impact_value = await self.get_impact_value(impact)
        if impact_value in impact_values:
            return ImpactEnum(impact_value)
        return None

    async def get_impact_value(self, impact):
        """Returns impact value"""
        return impact.attrs["class"][-1].split("--")[-1]

    async def get_event_values(
        self, element: element.Tag, class_name: str
    ) -> str:
        """Get event values"""
        data = element.find("td", {"class": class_name})
        return data.getText().strip() if data is not None else None

    async def get_actual_value(
        self, element: element.Tag, class_name: str
    ) -> Tuple[str, SentimentEnum]:
        """Get actual values and sentiment"""
        data = element.find("td", {"class": class_name})
        strength = await self.get_strength(data)
        return data.getText().strip(), strength

    async def get_strength(self, data):
        """Get strength"""
        span = data.find("span")
        if span:
            strength = span.attrs["class"][-1]
            strength = (
                SentimentEnum(strength)
                if strength in SentimentEnum._value2member_map_
                else SentimentEnum.FLAT
            )
            return strength
        return SentimentEnum.FLAT

    async def get_time_value(
        self, grouped_data: list[element.Tag], day_index, tag_index
    ) -> Union[None, datetime.time]:
        """Get the time value for an event"""
        time = None
        while not time:
            data = grouped_data[day_index][tag_index]
            value = await self.get_event_values(data, CALENDAR_TIME)
            if value != "":
                time = value
            tag_index -= 1

        try:
            # Get the local timezone
            local_timezone = get_localzone()
            local = timezone(local_timezone.zone)
            return (
                datetime.strptime(time, "%I:%M%p")
                .time()
                .replace(tzinfo=local.localize(datetime.now()).tzinfo)
            )
        except ValueError:
            return None

    async def get_absolute_value(self, value: str) -> float:
        """Get the absolute value of percentage value"""
        try:
            result = re.sub(r"[^0-9.]", "", value)
            return float(result)
        except ValueError:
            return None

    async def get_date_value(self, value: str) -> date:
        """Return the current date"""
        date = datetime.strptime(value, "%a%b %d").date()
        return datetime(datetime.today().year, date.month, date.day)

    async def create_fundamental_object(
        self, tag: element.Tag, date_time: datetime
    ):
        """create fundamental object"""
        currency = await self.get_event_values(
            element=tag, class_name=CALENDAR_CURRENCY
        )
        currency = CurrencyEnum(currency)
        return FundamentalData(currency=currency, last_updated=date_time)

    async def create_calendar_event(
        self,
        tag: element.Tag,
    ) -> Union[None, CalendarEvent]:
        """Create calendar object"""
        calendar_event = await self.get_event_values(
            element=tag, class_name=CALENDAR_EVENT
        )

        impact = await self.get_impact(element=tag)

        if impact != ImpactEnum.high:
            return None

        actual, sentiment = await self.get_actual_value(
            element=tag, class_name=CALENDAR_ACTUAL
        )
        actual = await self.get_absolute_value(actual)

        forecast = await self.get_event_values(
            element=tag, class_name=CALENDAR_FORECAST
        )
        forecast = await self.get_absolute_value(forecast)

        previous = await self.get_event_values(
            element=tag, class_name=CALENDAR_PREVIOUS
        )
        previous = await self.get_absolute_value(previous)

        return CalendarEvent(
            forecast=forecast,
            actual=actual,
            previous=previous,
            calendar_event=calendar_event,
            sentiment=sentiment,
        )

    async def get_scraped_event(
        self, grouped_data: list[element.Tag], day_index
    ):
        """Get scraped event"""
        # tag_index = len(grouped_data[day_index]) - 1
        # time = await self.get_time_value(
        #     grouped_data=grouped_data, day_index=day_index, tag_index=tag_index
        # )
        # calendar_event = await self.create_calendar_event(
        #     tag=grouped_data[day_index][tag_index]
        # )
        # fundamental_data = await self.create_fundamental_object(
        #     date_=await self.get_date_value(
        #         await self.get_event_values(
        #             grouped_data[day_index][tag_index], CALENDAR_DATE
        #         )
        #     ),
        #     tag=grouped_data[day_index][tag_index],
        #     time=time,
        # )
        # return CalendarEvent(
        #     fundamental_data=fundamental_data,
        #     calendar_event=calendar_event,
        #     time=time,
        # )
