import datetime
from src.config import CalendarEventEnum, CurrencyEnum
from src.models.db_connect import Database, context
from src.classes.fundamental import FundamentalData, FundamentalTrend
from hypothesis.strategies import from_type
from hypothesis import given, settings, HealthCheck
from src.repositories.fundamental_repository import FundamentalDataRepository
from src.repositories.fundamental_trend_repository import (
    FundamentalTrendRepository,
)


class TestFundamentalOrm:
    @given(from_type(FundamentalData))
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_add_fundamental_data_to_db(self, get_db, data):
        repo = FundamentalDataRepository()
        currency = data.currency
        last_updated = data.last_updated
        with get_db.session() as session:
            context.set(session)
            repo.add(data)

        with get_db.session() as session:
            context.set(session)
            objs = repo.get_all()
            assert len(objs) > 0
            fundamental_data = repo.get_fundamental_data(
                currency, last_updated
            )
            assert fundamental_data is not None


class TestTrendOrm:
    @given(from_type(FundamentalData))
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_add_trend_data_to_db(self, get_db, data):
        """Test adding trend to the db"""
        currency = data.currency
        last_updated = data.last_updated
        repo = FundamentalTrendRepository()
        with get_db.session() as session:
            context.set(session)
            repo.add(data)
        with get_db.session() as session:
            context.set(session)
            trend = FundamentalTrend(
                last_updated=last_updated, currency=currency
            )
            repo.add(trend)

        with get_db.session() as session:
            context.set(session)
            trend = repo.get_all()
            assert len(trend) > 0
            assert isinstance(trend[-1].fundamental_data, FundamentalData)
