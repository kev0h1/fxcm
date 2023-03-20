import itertools
from typing import Tuple, Union
from bs4 import BeautifulSoup, element
from src.classes.fundamental import CalendarEvent, FundamentalData
import requests
from datetime import datetime, time, date
from src.config import (
    CalendarEventEnum,
    CurrencyEnum,
    ImpactEnum,
    SentimentEnum,
)
import re
from src.errors.errors import (
    InvalidEventTypeException,
    NoEconomicImpactDefined,
)
from pytz import timezone

URL = "https://www.forexfactory.com/calendar"
CALENDAR_ACTUAL = "calendar__actual"
CALENDAR_FORECAST = "calendar__forecast"
CALENDAR_PREVIOUS = "calendar__previous"
CALENDAR_EVENT = "calendar__event"
CALENDAR_TIME = "calendar__time"
CALENDAR_DAY = "calendar__cell"
CALENDAR_CURRENCY = "calendar__currency"


class ForexFactoryScraper:
    def __init__(self, url: str):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0"
        }
        page = requests.get(url, headers=headers, verify=False)
        self.soup = BeautifulSoup(page.content, "html.parser")

    @staticmethod
    def get_correct_date_format(date_: datetime = datetime.today()):
        """Get the correct day format"""
        return date_.strftime("%b%d.%Y")

    @staticmethod
    def get_url_for_today(date_: datetime = datetime.today()):
        """Get the url to search for today"""
        today = ForexFactoryScraper.get_correct_date_format(date_=date_)
        return "%s?day=%s" % (URL, today)

    def __get_calendar_objects(self) -> element.ResultSet:
        """Get all calendar objects"""
        return self.soup.find_all("tr", {"class": "calendar__row"})

    def __filter_expand_objects(
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

    def __group_list_by_date(self, data: list) -> list:
        """Groups the data by date
        This follows filtering of the unwanted data
        """
        items = itertools.groupby(
            data, lambda tr: "calendar__row--day-breaker" in tr["class"]
        )

        return [list(i) for _, i in items]

    def get_fundamental_items(self):
        """Return fundamental data to iterate"""
        objects = self.__get_calendar_objects()
        filtered_objects = self.__filter_expand_objects(objects)
        return self.__group_list_by_date(filtered_objects)

    def get_impact(self, element: element.Tag) -> str:
        """Get the impact of the news"""
        impact_values = ["low", "medium", "high"]
        impact = element.find("td", {"class": "calendar__impact"})
        if impact is None:
            raise NoEconomicImpactDefined("Cannot determine impact")
        impact_value = self.get_impact_value(impact)
        if impact_value in impact_values:
            return ImpactEnum(impact_value)
        return None

    def get_impact_value(self, impact):
        """Returns impact value"""
        return impact.attrs["class"][-1].split("--")[-1]

    def get_fundamental_performance(self, element: element.Tag):
        """Get the performance of a news item"""

    def get_event_values(self, element: element.Tag, class_name: str) -> str:
        """Get event values"""
        data = element.find("td", {"class": class_name})
        return data.getText().strip() if data is not None else None

    def get_actual_value(
        self, element: element.Tag, class_name: str
    ) -> Tuple[str, SentimentEnum]:
        """Get actual values and sentiment"""
        data = element.find("td", {"class": class_name})
        strength = self.get_strength(data)
        return data.getText().strip(), strength

    def get_strength(self, data):
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

    def get_time_value(
        self, grouped_data: list[element.Tag], day_index, tag_index
    ) -> Union[None, datetime.time]:
        """Get the time value for an event"""
        time = None
        while not time:
            data = grouped_data[day_index][tag_index]
            value = self.get_event_values(data, CALENDAR_TIME)
            if value is not "":
                time = value
            tag_index -= 1

        if time != "All Day":
            eastern = timezone("US/Eastern")
            return (
                datetime.strptime(time, "%H:%M%p")
                .time()
                .replace(tzinfo=eastern.localize(datetime.now()).tzinfo)
            )
        return None

    def get_absolute_value(self, value: str) -> float:
        """Get the absolute value of percentage value"""
        try:
            result = re.sub(r"[^0-9.]", "", value)
            return float(result)
        except ValueError:
            return None

    def get_date_value(self, value: str) -> date:
        """Return the current date"""
        date = datetime.strptime(value, "%a%b %d").date()
        return datetime(datetime.today().year, date.month, date.day)

    def create_fundamental_object(
        self, date_: date, tag: element.Tag, time: time
    ):
        """create fundamental object"""
        if not time:
            return None
        time_ = time
        date_time = datetime.combine(date_, time_)

        currency = self.get_event_values(
            element=tag, class_name=CALENDAR_CURRENCY
        )
        currency = CurrencyEnum(currency)
        return FundamentalData(currency=currency, last_updated=date_time)

    def create_calendar_event(
        self,
        tag: element.Tag,
    ) -> Union[None, FundamentalData]:
        """Create calendar object"""
        calendar_event = self.get_event_values(
            element=tag, class_name=CALENDAR_EVENT
        )

        impact = self.get_impact(element=tag)

        if impact != ImpactEnum.high:
            return None

        actual, sentiment = self.get_actual_value(
            element=tag, class_name=CALENDAR_ACTUAL
        )
        actual = self.get_absolute_value(actual)

        forecast = self.get_event_values(
            element=tag, class_name=CALENDAR_FORECAST
        )
        forecast = self.get_absolute_value(forecast)

        previous = self.get_event_values(
            element=tag, class_name=CALENDAR_PREVIOUS
        )
        previous = self.get_absolute_value(previous)

        return CalendarEvent(
            forecast=forecast,
            actual=actual,
            previous=previous,
            calendar_event=calendar_event,
            sentiment=sentiment,
        )
