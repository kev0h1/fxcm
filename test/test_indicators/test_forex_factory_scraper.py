import os
from src.config import SentimentEnum
from src.indicators.forex_factory_scraper import (
    ForexFactoryScraper,
    requests,
    BeautifulSoup,
    element,
    NoEconomicImpactDefined,
    CALENDAR_CURRENCY,
    CALENDAR_DAY,
    CALENDAR_EVENT,
    CALENDAR_FORECAST,
    CALENDAR_ACTUAL,
    datetime,
    FundamentalData,
    InvalidEventTypeException,
    CalendarEventEnum,
    URL,
)
import re
from datetime import time
import mock
import pytest
from requests import Response

file = os.path.abspath(os.curdir) + "/test/context_1_day.txt"
with open(file, "rb") as f:
    page = f.read()


class MockResponse(Response):
    def __init__(self) -> None:
        super().__init__()
        self._content = page


with mock.patch.object(requests, "get", return_value=MockResponse()) as get:
    scraper = ForexFactoryScraper(url="test.com")


class TestForexFactoryScraper:
    class TestInit:
        def test_init(self):
            """Test the init method"""
            with mock.patch.object(
                requests, "get", return_value=MockResponse()
            ) as get, mock.patch.object(
                BeautifulSoup, "__init__", return_value=None
            ) as soup:
                ForexFactoryScraper(url="test.com")
                get.assert_called_once()
                soup.assert_called_once()

    class TestGetFundamentalItems:
        def test_get_fundamental_items(self):
            """Test the retrival of the fundamental data items"""
            grouped_data = scraper.get_fundamental_items()
            assert len(grouped_data) > 0

    class TestGetImpact:
        def test_get_impact(self):
            grouped_data = scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            impact = scraper.get_impact(data)
            assert impact == "low"

        def test_get_impact_fails(self):
            grouped_data = scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            with mock.patch.object(
                element.Tag, "find", return_value=None
            ), pytest.raises(NoEconomicImpactDefined):
                _ = scraper.get_impact(data)

        def test_get_impact_fails_for_invalid_impact(self):
            grouped_data = scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            with mock.patch.object(
                element.Tag, "find", return_value=None
            ), mock.patch.object(
                ForexFactoryScraper, "get_impact_value", return_value="risk"
            ) as get, pytest.raises(
                NoEconomicImpactDefined
            ):
                _ = scraper.get_impact(data)
                get.assert_called_once()

    class TestGetEventValues:
        def test_get_event_values(self):
            """Test get event value for impact object"""
            grouped_data = scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            assert len(scraper.get_event_values(data, CALENDAR_CURRENCY)) > 0
            assert len(scraper.get_event_values(data, CALENDAR_EVENT)) > 0

        def test_get_day_event_values_fails_for_impact_object(self):
            """Get day event value fails for impact object"""
            grouped_data = scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            assert len(scraper.get_event_values(data, CALENDAR_DAY)) == 0

        def test_get_day_event_values_passes_for_daybreak_object(self):
            """Get day event value passes for day break object"""
            grouped_data = scraper.get_fundamental_items()
            data = grouped_data[0][0]
            assert len(scraper.get_event_values(data, CALENDAR_DAY)) > 0

    class TestGetActualValue:
        def test_get_actual_value(self):
            """Test get actual value"""
            grouped_data = scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            actual, sentiment = scraper.get_actual_value(data, CALENDAR_ACTUAL)
            assert isinstance(actual, str)
            assert isinstance(sentiment, SentimentEnum)

    class TestGetAbsoluteValue:
        def test_get_absolute_value(self):
            """Test the retrival of absolute of the value"""
            grouped_data = scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            value = scraper.get_event_values(data, CALENDAR_FORECAST)
            val = scraper.get_absolute_value(value=value)
            assert isinstance(val, float)

        def test_get_absolute_value_returns_none_if_invalid(self):
            """Test the retrival of absolute of the value"""
            val = scraper.get_absolute_value(value="")
            assert val is None

    class TestGetTimeValue:
        def test_get_time_value(self):
            """Test get time value"""
            grouped_data = scraper.get_fundamental_items()
            time_ = scraper.get_time_value(grouped_data, -1, -1)
            assert isinstance(time_, time)

    class TestGetDateValue:
        def test_get_date_value(self):
            """Get date value"""
            value = "WedDec 7"
            date_ = scraper.get_date_value(value)
            assert date_.day == 7
            assert date_.month == 12
            assert date_.year == datetime.today().year

    class TestGetEventType:
        def test_get_event_type_raises_exception(self):
            """Test raised exception for invalid event"""
            value = "boo y/y"
            with pytest.raises(InvalidEventTypeException):
                val = scraper.get_event_type(value)

        def test_get_event_type(self):
            """Test the retrival of an event"""
            value = "CPI y/y"
            val = scraper.get_event_type(value)
            assert isinstance(val, CalendarEventEnum)

    class TestCreateFundamentalDataObject:
        def test_create_fundamental_data_object_with_invalid_event(self):
            """Test the creation of the fundamental object"""
            grouped_data = scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            day_break = grouped_data[0][0]

            obj = scraper.create_fundamental_data_object(day_break, data)
            assert obj is None

        def test_create_fundamental_data_object_with_valid_event(self):
            """Test the creation of the fundamental object"""
            grouped_data = scraper.get_fundamental_items()
            data = grouped_data[-1][-1]

            day_break = grouped_data[0][0]
            with mock.patch.object(
                ForexFactoryScraper,
                "get_event_type",
                return_value=CalendarEventEnum.CPI_M,
            ), mock.patch.object(
                ForexFactoryScraper,
                "get_time_value",
                return_value=datetime.today().time(),
            ):
                time_ = scraper.get_time_value(grouped_data, -1, -4)
                obj = scraper.create_fundamental_data_object(
                    datetime.today(), data, time_
                )
            assert isinstance(obj, FundamentalData)

        def test_create_fundamental_data_object_for_bank_holiday(self):
            """Test the creation of the fundamental object"""
            grouped_data = scraper.get_fundamental_items()
            data = grouped_data[-1][-1]

            day_break = grouped_data[0][0]
            with mock.patch.object(
                ForexFactoryScraper,
                "get_event_type",
                return_value=CalendarEventEnum.CPI_M,
            ), mock.patch.object(
                ForexFactoryScraper,
                "get_time_value",
                return_value=None,
            ):
                time_ = scraper.get_time_value(grouped_data, -1, -4)
                obj = scraper.create_fundamental_data_object(
                    day_break, data, time_
                )
            assert obj is None

        def test_create_fundamental_data_object_with_invalid_event(self):
            """Test the creation of the fundamental object"""
            grouped_data = scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            time_ = scraper.get_time_value(grouped_data, -1, -4)
            day_break = grouped_data[0][0]
            obj = scraper.create_fundamental_data_object(
                day_break, data, time_
            )
            assert obj is None

    class TestGetCorrectDateFormat:
        def test_get_correct_date_format(self):
            """Tests the retrieval of the correct date format"""
            date_ = ForexFactoryScraper.get_correct_date_format()
            assert len(re.findall("[a-zA-Z]{3}[0-9]{2}[.][0-9]{4}", date_)) > 0

    class TestGetUrlForToday:
        def test_get_url_for_today(self):
            """Test getting the url for today"""
            url = ForexFactoryScraper.get_url_for_today()
            assert len(re.findall("[a-zA-Z]{3}[0-9]{2}[.][0-9]{4}", url)) > 0
            assert URL in url
