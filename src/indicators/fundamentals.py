import itertools
from typing import Union
from bs4 import BeautifulSoup, element
from src.classes.trend import FundamentalData
import requests
from datetime import datetime, time, date
from src.config import CalendarEventEnum, CurrencyEnum

from src.errors.errors import NoEconomicImpactDefined

URL = "https://www.forexfactory.com/calendar"
CALENDAR_ACTUAL = "calendar__actual"
CALENDAR_FORECAST = "calendar__forecast"
CALENDAR_PREVIOUS = "calendar__previous"
CALENDAR_EVENT = "calendar__event"
CALENDAR_TIME = "calendar__time"
CALENDAR_DAY = "calendar__cell"
CALENDAR_CURRENCY = "calendar__currency"
trim_list = ["y/y", "m/m", "q/q"]


class ForexFactoryScraper:
    def __init__(self, url: str = URL):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0"
        }
        page = requests.get(url, headers=headers, verify=False)
        self.soup = BeautifulSoup(page.content, "html.parser")

    def get_calendar_objects(self) -> element.ResultSet:
        """Get all calendar objects"""
        return self.soup.find_all("tr", {"class": "calendar__row"})

    def filter_expand_objects(
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

    def group_list_by_date(self, data: list) -> list:
        """Groups the data by date
        This follows filtering of the unwanted data
        """
        return itertools.groupby(
            data, lambda tr: "calendar__row--day-breaker" in tr["class"]
        )

    def get_impact(self, element: element.Tag) -> str:
        """Get the impact of the news"""
        impact_values = ["low", "medium", "high"]
        impact = element.find("td", {"class": "calendar__impact"})
        if impact is None:
            raise NoEconomicImpactDefined("Cannot determine impact")
        impact_value = impact.attrs["class"][-1].split("--")
        if impact_value in impact_values:
            return impact_value
        raise NoEconomicImpactDefined("Undefined impact")

    def get_event_values(self, element: element.Tag, class_name: str) -> str:
        """Get event values"""
        data = element.find("td", {"class": class_name})
        return data.getText().strip()

    def get_absolute_value(self, value: str) -> float:
        """Get the absolute value of percentage value"""
        return float(value.strip("%"))

    def get_time_value(self, value: str) -> time:
        """Return the time value"""
        return datetime.strptime(value, "%H:%M%p").time()

    def get_date_value(self, value: str) -> date:
        """Return the current date"""
        date = datetime.strptime(value, "%a%b %d").date()
        return datetime(datetime.today().year, date.month, date.day)

    def remove_period_values(self, value: str) -> str:
        """Remove period markers for event"""
        return " ".join(
            [
                f
                for f in filter(
                    lambda x: x if x not in trim_list else None,
                    value.split(" "),
                )
            ]
        )

    def create_fundamental_data_object(
        self, day_tag: element.Tag, tag: element.Tag
    ) -> Union[None, FundamentalData]:
        """Create fundamental data object"""
        calendar_event = self.get_event_values(
            element=day_tag, class_name=CALENDAR_EVENT
        )
        calendar_event = self.remove_period_values(calendar_event)

        if calendar_event not in CalendarEventEnum:
            return None

        day_value = self.get_event_values(element=tag, class_name=CALENDAR_DAY)
        date_ = self.get_date_value(day_value)

        time_value = self.get_event_values(
            element=tag, class_name=CALENDAR_TIME
        )
        time_ = self.get_time_value(time_value)

        date_time = datetime.combine(date_, time_)

        actual = self.get_event_values(element=tag, class_name=CALENDAR_ACTUAL)
        actual = self.get_absolute_value(actual)

        forecast = self.get_event_values(
            element=tag, class_name=CALENDAR_FORECAST
        )
        forecast = self.get_absolute_value(forecast)

        previous = self.get_event_values(
            element=tag, class_name=CALENDAR_PREVIOUS
        )
        previous = self.get_absolute_value(previous)

        currency = self.get_event_values(
            element=tag, class_name=CALENDAR_CURRENCY
        )
        currency = CurrencyEnum(currency)

        return FundamentalData(
            currency=currency,
            last_updated=date_time,
            forecast=forecast,
            actual=actual,
            previous=previous,
            calendar_event=CalendarEventEnum(calendar_event),
        )


data = ForexFactoryScraper()
# with open("output1.html", "w") as file:
#     file.write(str(data.soup))
print("hi")
