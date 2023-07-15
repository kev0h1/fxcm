from datetime import datetime
from src.adapters.fxcm_connect.mock_trade_connect import MockTradeConnect
from src.adapters.scraper.mock_scraper import MockScraper
from src.config import CurrencyEnum, SentimentEnum
from src.domain.fundamental import CalendarEvent, FundamentalData
from src.service_layer.uow import MongoUnitOfWork
from src.service_layer.fundamental_service import FundamentalDataService
from src.entry_points.scheduler.get_fundamental_data import (
    process_data,
    get_calendar_event,
)
import pytest
from src.domain.events import CloseTradeEvent


class TestGetFundamentalData:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "sentiment",
        [SentimentEnum.BEARISH, SentimentEnum.BULLISH, SentimentEnum.FLAT],
    )
    async def test_process_data_for_events(
        self, sentiment: SentimentEnum
    ) -> None:
        uow = MongoUnitOfWork(
            fxcm_connection=MockTradeConnect(),
            scraper=MockScraper(sentiment=sentiment),
        )

        fundamental_service = FundamentalDataService(uow=uow)
        await process_data(
            date_=datetime.now(),
            uow=uow,
            fundamental_data_service=fundamental_service,
        )
        if sentiment == SentimentEnum.FLAT:
            assert uow.event_bus.queue.empty()
        else:
            event = await uow.event_bus.queue.get()
            assert isinstance(event, CloseTradeEvent)
            assert event.sentiment == sentiment

    @pytest.mark.asyncio
    async def test_process_data_for_processed_events(self) -> None:
        uow = MongoUnitOfWork(
            fxcm_connection=MockTradeConnect(),
            scraper=MockScraper(
                sentiment=SentimentEnum.BULLISH, is_processed=True
            ),
        )
        fundamental_service = FundamentalDataService(uow=uow)
        await process_data(
            date_=datetime.now(),
            uow=uow,
            fundamental_data_service=fundamental_service,
        )
        assert uow.event_bus.queue.empty()


class TestGetCalendarEvent:
    @pytest.mark.asyncio
    async def test_get_calendar_event(self) -> None:
        test_event = CalendarEvent(
            calendar_event="mock_event",
            sentiment=SentimentEnum.BULLISH,
            forecast=1.2,
            actual=1.3,
            previous=1.1,
        )

        test_event_2 = CalendarEvent(
            calendar_event="t2",
            sentiment=SentimentEnum.BULLISH,
            forecast=1.2,
            actual=1.3,
            previous=1.1,
        )
        fundamental_data = FundamentalData(
            currency=CurrencyEnum.USD,
            last_updated=datetime.now(),
            calendar_events=[test_event],
            processed=False,
        )

        event = await get_calendar_event(
            fundamental_data=fundamental_data, calendar_event=test_event
        )
        assert event is not None
        test_event.calendar_event = "mock_event2"
        event = await get_calendar_event(
            fundamental_data=fundamental_data, calendar_event=test_event_2
        )
        assert event is None
