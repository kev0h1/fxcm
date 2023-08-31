import pandas as pd
from src.adapters.fxcm_connect.mock_trade_connect import MockTradeConnect
from src.config import SentimentEnum
from src.domain.events import CloseForexPairEvent, OpenTradeEvent
from src.entry_points.scheduler.get_technical_signal import (
    get_signal,
    get_technical_signal,
)
import pytest
import mock
from src.service_layer.indicators import Indicators

from src.service_layer.uow import MongoUnitOfWork


@pytest.mark.skip
class TestGetTechnicalSignal:
    @pytest.mark.asyncio
    async def test_get_technical_signal_for_buy(self) -> None:
        data_frame = pd.DataFrame(
            [
                {
                    "ShortTerm_MA": 0.5,
                    "MediumTerm_MA": 0.4,
                    "LongTerm_MA": 0.1,
                    "Prev_ShortTerm_MA": 0.4,
                    "Prev_MediumTerm_MA": 0.5,
                    "rsi": 29,
                }
            ]
        )
        data_frame: pd.DataFrame = await get_signal(data_frame)
        assert data_frame.iloc[-1]["Signal"] == 1

    @pytest.mark.asyncio
    async def test_get_technical_signal_for_buy_event(self, get_db) -> None:
        data_frame = pd.DataFrame(
            [
                {
                    "ShortTerm_MA": 0.5,
                    "MediumTerm_MA": 0.4,
                    "LongTerm_MA": 0.1,
                    "Prev_ShortTerm_MA": 0.4,
                    "Prev_MediumTerm_MA": 0.5,
                    "rsi": 29,
                    "close": 1.2,
                }
            ]
        )
        data_frame = await get_signal(data_frame)
        with mock.patch(
            "src.entry_points.scheduler.get_technical_signal.get_signal"
        ) as mock_get_signal:
            mock_get_signal.return_value = data_frame
            uow = MongoUnitOfWork(
                fxcm_connection=MockTradeConnect(),
                scraper=mock.MagicMock(),
                db_name=get_db,
            )
            await get_technical_signal(uow=uow, indicator=Indicators())
            event = await uow.event_bus.queue.get()
            assert isinstance(event, CloseForexPairEvent)
            assert event.sentiment == SentimentEnum.BEARISH

            event = await uow.event_bus.queue.get()
            assert isinstance(event, OpenTradeEvent)
            assert event.sentiment == SentimentEnum.BULLISH

    @pytest.mark.asyncio
    async def test_get_technical_signal_for_sell(self) -> None:
        data_frame = pd.DataFrame(
            [
                {
                    "ShortTerm_MA": 0.4,
                    "MediumTerm_MA": 0.5,
                    "LongTerm_MA": 0.9,
                    "Prev_ShortTerm_MA": 0.5,
                    "Prev_MediumTerm_MA": 0.4,
                    "rsi": 89,
                }
            ]
        )
        data_frame: pd.DataFrame = await get_signal(data_frame)
        assert data_frame.iloc[-1]["Signal"] == -1

    @pytest.mark.asyncio
    async def test_get_technical_signal_for_sell_event(self, get_db) -> None:
        data_frame = pd.DataFrame(
            [
                {
                    "ShortTerm_MA": 0.4,
                    "MediumTerm_MA": 0.5,
                    "LongTerm_MA": 0.9,
                    "Prev_ShortTerm_MA": 0.5,
                    "Prev_MediumTerm_MA": 0.4,
                    "rsi": 89,
                    "close": 1.2,
                }
            ]
        )
        data_frame = await get_signal(data_frame)
        with mock.patch(
            "src.entry_points.scheduler.get_technical_signal.get_signal"
        ) as mock_get_signal:
            mock_get_signal.return_value = data_frame
            uow = MongoUnitOfWork(
                fxcm_connection=MockTradeConnect(),
                scraper=mock.MagicMock(),
                db_name=get_db,
            )
            await get_technical_signal(uow=uow, indicator=Indicators())
            event = await uow.event_bus.queue.get()
            assert isinstance(event, CloseForexPairEvent)
            assert event.sentiment == SentimentEnum.BULLISH

            event = await uow.event_bus.queue.get()
            assert isinstance(event, OpenTradeEvent)
            assert event.sentiment == SentimentEnum.BEARISH
