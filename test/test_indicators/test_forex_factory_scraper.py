import os
from src.indicators.forex_factory_scraper import (
    ForexFactoryScraper,
    requests,
    BeautifulSoup,
    element,
    NoEconomicImpactDefined,
    CALENDAR_ACTUAL,
    CALENDAR_CURRENCY,
    CALENDAR_DAY,
    CALENDAR_EVENT,
    CALENDAR_FORECAST,
    CALENDAR_PREVIOUS,
    CALENDAR_TIME,
    datetime,
    FundamentalData,
)
import mock
import pytest
from requests import Response

file = os.path.abspath(os.curdir) + "/test/content.txt"
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

    class TestGetCalendarObjects:
        def test_get_calendar_objects(self):
            """Test the retrieval of the calendar objects"""
            list_ = scraper.get_calendar_objects()
            assert len(list_) > 0

    class TestFilterExpandObjects:
        def test_filter_expand_objects(self):
            """Test that we remove the unnecessary objects"""
            list_ = scraper.get_calendar_objects()
            filtered_list = scraper.filter_expand_objects(list_)
            assert len(list_) > len(filtered_list)

    class TestGroupListByDate:
        def test_group_list_by_date(self):
            list_ = scraper.get_calendar_objects()
            filtered_list = scraper.filter_expand_objects(list_)
            grouped_data = scraper.group_list_by_date(filtered_list)
            assert len(list_) > len(filtered_list) > len(grouped_data)

    class TestGetImpact:
        def test_get_impact(self):
            list_ = scraper.get_calendar_objects()
            filtered_list = scraper.filter_expand_objects(list_)
            grouped_data = scraper.group_list_by_date(filtered_list)
            data = grouped_data[3][9]
            impact = scraper.get_impact(data)
            assert impact == "low"

        def test_get_impact_fails(self):
            list_ = scraper.get_calendar_objects()
            filtered_list = scraper.filter_expand_objects(list_)
            grouped_data = scraper.group_list_by_date(filtered_list)
            data = grouped_data[3][9]
            with mock.patch.object(
                element.Tag, "find", return_value=None
            ), pytest.raises(NoEconomicImpactDefined):
                _ = scraper.get_impact(data)

        def test_get_impact_fails_for_invalid_impact(self):
            list_ = scraper.get_calendar_objects()
            filtered_list = scraper.filter_expand_objects(list_)
            grouped_data = scraper.group_list_by_date(filtered_list)
            data = grouped_data[3][9]
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
            list_ = scraper.get_calendar_objects()
            filtered_list = scraper.filter_expand_objects(list_)
            grouped_data = scraper.group_list_by_date(filtered_list)
            data = grouped_data[3][9]
            assert len(scraper.get_event_values(data, CALENDAR_TIME)) > 0
            assert len(scraper.get_event_values(data, CALENDAR_ACTUAL)) > 0
            assert len(scraper.get_event_values(data, CALENDAR_CURRENCY)) > 0
            assert len(scraper.get_event_values(data, CALENDAR_EVENT)) > 0
            assert len(scraper.get_event_values(data, CALENDAR_FORECAST)) > 0
            assert len(scraper.get_event_values(data, CALENDAR_PREVIOUS)) > 0

        def test_get_day_event_values_fails_for_impact_object(self):
            """Get day event value fails for impact object"""
            list_ = scraper.get_calendar_objects()
            filtered_list = scraper.filter_expand_objects(list_)
            grouped_data = scraper.group_list_by_date(filtered_list)
            data = grouped_data[3][9]
            assert len(scraper.get_event_values(data, CALENDAR_DAY)) == 0

        def test_get_day_event_values_passes_for_daybreak_object(self):
            """Get day event value passes for day break object"""
            list_ = scraper.get_calendar_objects()
            filtered_list = scraper.filter_expand_objects(list_)
            grouped_data = scraper.group_list_by_date(filtered_list)
            data = grouped_data[0][0]
            assert len(scraper.get_event_values(data, CALENDAR_DAY)) > 0

    class TestGetAbsoluteValue:
        def test_get_absolute_value(self):
            """Test the retrival of absolute of the value"""
            list_ = scraper.get_calendar_objects()
            filtered_list = scraper.filter_expand_objects(list_)
            grouped_data = scraper.group_list_by_date(filtered_list)
            data = grouped_data[3][9]
            value = scraper.get_event_values(data, CALENDAR_FORECAST)
            val = scraper.get_absolute_value(value=value)
            assert isinstance(val, float)

    class TestGetTimeValue:
        def test_get_time_value(self):
            """Test get time value"""
            list_ = scraper.get_calendar_objects()
            filtered_list = scraper.filter_expand_objects(list_)
            grouped_data = scraper.group_list_by_date(filtered_list)
            data = grouped_data[3][9]
            value = scraper.get_event_values(data, CALENDAR_TIME)
            time_ = scraper.get_time_value(value)
            assert time_.hour == 6
            assert time_.minute == 50

    class TestGetDateValue:
        def test_get_date_value(self):
            """Get date value"""
            list_ = scraper.get_calendar_objects()
            filtered_list = scraper.filter_expand_objects(list_)
            grouped_data = scraper.group_list_by_date(filtered_list)
            data = grouped_data[0][0]
            value = scraper.get_event_values(data, CALENDAR_DAY)
            date_ = scraper.get_date_value(value)
            assert date_.day == 25
            assert date_.month == 12
            assert date_.year == datetime.today().year

    class TestRemovePeriodValues:
        def test_remove_period_values(self):
            """Test removal of period values"""
            list_ = scraper.get_calendar_objects()
            filtered_list = scraper.filter_expand_objects(list_)
            grouped_data = scraper.group_list_by_date(filtered_list)
            data = grouped_data[3][9]
            value = scraper.get_event_values(data, CALENDAR_EVENT)
            assert "y/y" in value
            val = scraper.remove_period_values(value)
            assert "y/y" not in val

    class TestCreateFundamentalDataObject:
        def test_create_fundamental_data_object_with_invalid_event(self):
            """Test the creation of the fundamental object"""
            list_ = scraper.get_calendar_objects()
            filtered_list = scraper.filter_expand_objects(list_)
            grouped_data = scraper.group_list_by_date(filtered_list)
            data = grouped_data[3][9]
            day_break = grouped_data[0][0]

            obj = scraper.create_fundamental_data_object(day_break, data)
            assert obj is None

        def test_create_fundamental_data_object_with_invalid_event(self):
            """Test the creation of the fundamental object"""
            list_ = scraper.get_calendar_objects()
            filtered_list = scraper.filter_expand_objects(list_)
            grouped_data = scraper.group_list_by_date(filtered_list)
            data = grouped_data[3][9]
            day_break = grouped_data[0][0]
            with mock.patch.object(
                ForexFactoryScraper, "remove_period_values", return_value="CPI"
            ):
                obj = scraper.create_fundamental_data_object(day_break, data)
            assert isinstance(obj, FundamentalData)
