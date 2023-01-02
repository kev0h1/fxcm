import datetime
from src.config import CalendarEventEnum, CurrencyEnum
from src.models.db_connect import DbSession
from src.classes.fundamental import FundamentalData, FundamentalTrend
from hypothesis.strategies import from_type
from hypothesis import given, settings


class TestFundamentalOrm:
    @given(from_type(FundamentalData))
    @settings(max_examples=1)
    def test_add_fundamental_data_to_db(self, data):
        with DbSession.session.begin() as session:
            session.add(data)

        with DbSession.session.begin() as session:
            objs = FundamentalData.get_all_fundamental_data(session)
            assert len(objs) > 0


class TestTrendOrm:
    @given(from_type(FundamentalData))
    @settings(max_examples=1)
    def test_add_trend_data_to_db(self, data):
        """Test adding trend to the db"""
        currency = data.currency
        last_updated = data.last_updated
        with DbSession.session.begin() as session:
            session.add(data)
        with DbSession.session.begin() as session:
            trend = FundamentalTrend(
                last_updated=last_updated, currency=currency
            )
            session.add(trend)
            print("hi")

        with DbSession.session.begin() as session:
            trend = FundamentalTrend.get_trend_data(session=session)
            assert len(trend) > 0
            assert isinstance(trend[-1].fundamental_data, FundamentalData)
