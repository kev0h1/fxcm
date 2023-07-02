import os
from src.domain.fundamental import CalendarEvent
from src.config import ImpactEnum, SentimentEnum
from src.adapters.scraper.forex_factory_scraper import (
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
    URL,
)
import re
from datetime import time
import mock
import pytest
from requests import Response


with open("test/context_1_day.txt", "r") as f:
    contents = f.read()
    soup = BeautifulSoup(contents, "html.parser")
    scraper = ForexFactoryScraper()
    scraper.soup = soup


class TestForexFactoryScraper:
    class TestGetFundamentalItems:
        @pytest.mark.asyncio
        async def test_get_fundamental_items(self):
            """Test the retrival of the fundamental data items"""
            grouped_data = await scraper.get_fundamental_items()
            assert len(grouped_data) > 0

    class TestGetImpact:
        @pytest.mark.asyncio
        async def test_get_impact(self):
            grouped_data = await scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            impact = await scraper.get_impact(data)
            assert impact == ImpactEnum.low

        @pytest.mark.asyncio
        async def test_get_impact_fails(self):
            grouped_data = await scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            with mock.patch.object(
                element.Tag, "find", return_value=None
            ), pytest.raises(NoEconomicImpactDefined):
                _ = await scraper.get_impact(data)

        @pytest.mark.asyncio
        async def test_get_impact_fails_for_invalid_impact(self):
            grouped_data = await scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            with mock.patch.object(
                element.Tag, "find", return_value=None
            ), mock.patch.object(
                ForexFactoryScraper, "get_impact_value", return_value="risk"
            ) as get, pytest.raises(
                NoEconomicImpactDefined
            ):
                _ = await scraper.get_impact(data)
                get.assert_called_once()

    class TestGetEventValues:
        @pytest.mark.asyncio
        async def test_get_event_values(self):
            """Test get event value for impact object"""
            grouped_data = await scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            assert (
                len(await scraper.get_event_values(data, CALENDAR_CURRENCY))
                > 0
            )
            assert (
                len(await scraper.get_event_values(data, CALENDAR_EVENT)) > 0
            )

        @pytest.mark.asyncio
        async def test_get_day_event_values_fails_for_impact_object(self):
            """Get day event value fails for impact object"""
            grouped_data = await scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            assert len(await scraper.get_event_values(data, CALENDAR_DAY)) == 0

        @pytest.mark.asyncio
        async def test_get_day_event_values_passes_for_daybreak_object(self):
            """Get day event value passes for day break object"""
            grouped_data = await scraper.get_fundamental_items()
            data = grouped_data[0][0]
            assert len(await scraper.get_event_values(data, CALENDAR_DAY)) > 0

    class TestGetActualValue:
        @pytest.mark.asyncio
        async def test_get_actual_value(self):
            """Test get actual value"""
            grouped_data = await scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            actual, sentiment = await scraper.get_actual_value(
                data, CALENDAR_ACTUAL
            )
            assert isinstance(actual, str)
            assert isinstance(sentiment, SentimentEnum)

    class TestGetAbsoluteValue:
        @pytest.mark.asyncio
        async def test_get_absolute_value(self):
            """Test the retrival of absolute of the value"""
            grouped_data = await scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            value = await scraper.get_event_values(data, CALENDAR_FORECAST)
            val = await scraper.get_absolute_value(value=value)
            assert isinstance(val, float)

        @pytest.mark.asyncio
        async def test_get_absolute_value_returns_none_if_invalid(self):
            """Test the retrival of absolute of the value"""
            val = await scraper.get_absolute_value(value="")
            assert val is None

    class TestGetTimeValue:
        @pytest.mark.asyncio
        async def test_get_time_value(self):
            """Test get time value"""
            grouped_data = await scraper.get_fundamental_items()
            time_ = await scraper.get_time_value(grouped_data, -1, -1)
            assert isinstance(time_, time)

    class TestGetDateValue:
        @pytest.mark.asyncio
        async def test_get_date_value(self):
            """Get date value"""
            value = "WedDec 7"
            date_ = await scraper.get_date_value(value)
            assert date_.day == 7
            assert date_.month == 12
            assert date_.year == datetime.today().year

    class TestCreateFundamentalDataObject:
        @pytest.mark.asyncio
        async def test_create_fundamental_data_object(self):
            """Test the creation of the fundamental object"""
            grouped_data = await scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            with mock.patch.object(
                ForexFactoryScraper,
                "get_time_value",
                return_value=datetime.today().time(),
            ):
                time_ = await scraper.get_time_value(grouped_data, -1, -4)
                obj = await scraper.create_fundamental_object(
                    data, datetime.today()
                )
            assert isinstance(obj, FundamentalData)

    class TestCreateCalendarEventObject:
        @pytest.mark.asyncio
        async def test_create_calendar_object_with_invalid_event(self):
            """Test the creation of the fundamental object"""
            grouped_data = await scraper.get_fundamental_items()
            data = grouped_data[-1][-1]

            obj = await scraper.create_calendar_event(data)
            assert obj is None

        @pytest.mark.asyncio
        async def test_create_calendar_object_with_high_impact_event(self):
            """Test the creation of the fundamental object"""
            grouped_data = await scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            with mock.patch.object(
                ForexFactoryScraper,
                "get_time_value",
                return_value=datetime.today().time(),
            ), mock.patch.object(
                ForexFactoryScraper, "get_impact", return_value=ImpactEnum.high
            ):
                obj = await scraper.create_calendar_event(data)
            assert isinstance(obj, CalendarEvent)

        @pytest.mark.asyncio
        async def test_create_calendar_object_with_non_high_impact_event(self):
            """Test the creation of the fundamental object"""
            grouped_data = await scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            with mock.patch.object(
                ForexFactoryScraper,
                "get_time_value",
                return_value=datetime.today().time(),
            ), mock.patch.object(
                ForexFactoryScraper, "get_impact", return_value=ImpactEnum.low
            ):
                obj = await scraper.create_calendar_event(data)
            assert obj is None

        @pytest.mark.asyncio
        async def test_create_fundamental_data_object_with_invalid_event(self):
            """Test the creation of the fundamental object"""
            grouped_data = await scraper.get_fundamental_items()
            data = grouped_data[-1][-1]
            obj = await scraper.create_calendar_event(data)
            assert obj is None

    class TestGetCorrectDateFormat:
        @pytest.mark.asyncio
        async def test_get_correct_date_format(self):
            """Tests the retrieval of the correct date format"""
            date_ = await ForexFactoryScraper.get_correct_date_format()
            assert len(re.findall("[a-zA-Z]{3}[0-9]{2}[.][0-9]{4}", date_)) > 0

    class TestGetUrlForToday:
        @pytest.mark.asyncio
        async def test_get_url_for_today(self):
            """Test getting the url for today"""
            url = await ForexFactoryScraper.get_url_for_today(datetime.today())
            assert len(re.findall("[a-zA-Z]{3}[0-9]{2}[.][0-9]{4}", url)) > 0
            assert URL in url
