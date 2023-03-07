from src.config import CalendarEventEnum, CurrencyEnum, SentimentEnum
from src.classes.fundamental import CalendarEvent, FundamentalData
from hypothesis.strategies import builds, datetimes, floats, sampled_from, text
from hypothesis import given, settings, HealthCheck
from src.repositories.fundamental_repository import FundamentalDataRepository


class TestFundamentalOrm:
    @given(
        builds(
            FundamentalData,
            currency=sampled_from(CurrencyEnum),
            last_updated=datetimes(),
        )
    )
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_add_fundamental_data_to_db(self, get_db, data):
        repo = FundamentalDataRepository()
        currency = data.currency
        last_updated = data.last_updated
        with get_db.get_session():
            repo.save(data)
        with get_db.get_session():
            objs = repo.get_all()
            assert len(objs) > 0
        with get_db.get_session():
            fundamental_data = repo.get_fundamental_data(
                currency, last_updated
            )
            assert fundamental_data is not None

    @given(
        builds(
            FundamentalData,
            currency=sampled_from(CurrencyEnum),
            last_updated=datetimes(),
        ),
        builds(
            CalendarEvent,
            forecast=floats(),
            actual=floats(),
            previous=floats(),
            calendar_event=text(),
            sentiment=sampled_from(SentimentEnum),
        ),
    )
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    def test_add_calendar_events(self, get_db, data, calendar_event):
        repo = FundamentalDataRepository()
        currency = data.currency
        last_updated = data.last_updated
        data.calendar_events.append(calendar_event)
        calendar_event_name = calendar_event.calendar_event
        with get_db.get_session():
            repo.save(data)
        with get_db.get_session():
            fundamental_data = repo.get_fundamental_data(
                currency, last_updated
            )
            calendar_event = repo.get_calendar_event(
                fundamental_data, calendar_event=calendar_event_name
            )
            assert calendar_event is not None
