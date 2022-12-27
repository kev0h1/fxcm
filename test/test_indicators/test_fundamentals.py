import os
from bs4 import BeautifulSoup, element
import itertools

file = os.path.abspath(os.curdir) + "/test/soup.html"

with open(file, "r") as f:
    page_content = f.read()
soup = BeautifulSoup(page_content)


class TestFundamentals:
    class TestGetDailyData:
        def get_impact(self, element: element.Tag):
            impact_values = ["low", "medium", "high"]
            impact = element.find("td", {"class": "calendar__impact"})
            if impact is None:
                raise ValueError("Cannot determine impact")
            impact_value = impact.attrs["class"][-1].split("--")
            if impact_value in impact_values:
                return impact_value
            raise ValueError("Undefined impact")

        def get_event_values(self, element: element.Tag, class_name: str):
            data = element.find("td", {"class": class_name})
            return data.getText().strip()

        def test_get_daily_data(self):
            calendar_objects = soup.find_all("tr", {"class": "calendar__row"})
            group_func = lambda tr: "calendar__row--day-breaker" in tr["class"]
            filtered_rows = [
                f
                for f in filter(
                    lambda tr: "calendar__expand" not in tr["class"],
                    calendar_objects,
                )
            ]
            grouper = itertools.groupby(filtered_rows, group_func)
            result = [list(files) for _, files in grouper]
            test = result[3][9]
            print("hi")
