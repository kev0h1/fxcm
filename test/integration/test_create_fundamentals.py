import datetime
from src.config import CalendarEventEnum, CurrencyEnum
from src.models.db_connect import Database
from src.classes.fundamental import FundamentalData, FundamentalTrend
from hypothesis.strategies import from_type
from hypothesis import given, settings


class TestFundamentalOrm:
    @given(from_type(FundamentalData))
    @settings(max_examples=1)
    def test_add_fundamental_data_to_db(self, data):
        currency = data.currency
        last_updated = data.last_updated
        with Database.session.begin() as session:
            session.add(data)

        with Database.session.begin() as session:
            objs = FundamentalData.get_all_fundamental_data(session)
            assert len(objs) > 0
            fundamental_data = FundamentalData.get_fundamental_data(
                session, currency, last_updated
            )
            assert fundamental_data is not None


class TestTrendOrm:
    @given(from_type(FundamentalData))
    @settings(max_examples=1)
    def test_add_trend_data_to_db(self, data):
        """Test adding trend to the db"""
        currency = data.currency
        last_updated = data.last_updated
        with Database.session.begin() as session:
            session.add(data)
        with Database.session.begin() as session:
            trend = FundamentalTrend(
                last_updated=last_updated, currency=currency
            )
            session.add(trend)
            print("hi")

        with Database.session.begin() as session:
            trend = FundamentalTrend.get_trend_data(session=session)
            assert len(trend) > 0
            assert isinstance(trend[-1].fundamental_data, FundamentalData)
