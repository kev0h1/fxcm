import itertools
from bs4 import BeautifulSoup, element

import requests

from src.errors.errors import NoEconomicImpactDefined

URL = "https://www.forexfactory.com/calendar"


class FundamentalData:
    def __init__(self, url: str = URL):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0"
        }
        page = requests.get(url, headers=headers, verify=False)
        self.soup = BeautifulSoup(page.content, "html.parser")

    def set_calendar_objects(self) -> element.ResultSet:
        """Get all calendar objects"""
        return self.soup.find_all("tr", {"class": "calendar__row"})

    def filter_expand_objects(
        self, calendar_objects: element.ResultSet
    ) -> list:
        """Filter all expand objects"""
        return [
            f
            for f in filter(
                lambda tr: "calendar__expand" not in tr["class"],
                calendar_objects,
            )
        ]

    def group_list_by_date(self, data: list) -> list:
        """Groups the data by date"""
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


data = FundamentalData()
# with open("output1.html", "w") as file:
#     file.write(str(data.soup))
print("hi")
