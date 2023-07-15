from hypothesis import settings, given, HealthCheck
import mock
from src.adapters.database.mongo.trade_model import Trade
from src.adapters.fxcm_connect.mock_trade_connect import MockTradeConnect
from src.domain.events import CloseTradeEvent
from src.service_layer.event_bus import TradingEventBus
from src.service_layer.handlers import *
from src.config import CurrencyEnum, ForexPairEnum, SignalTypeEnum
import pytest
from src.domain.trade import Trade as TradeDomain
from hypothesis.strategies import (
    builds,
    integers,
    floats,
    sampled_from,
)


from src.service_layer.uow import MongoUnitOfWork


class TestCloseEventHandler:
    @pytest.mark.asyncio
    @given(
        builds(
            Trade,
            trade_id=integers(min_value=12),
            position_size=integers(),
            stop=floats(),
            limit=floats(),
            is_buy=sampled_from([False]),
            signal=sampled_from(SignalTypeEnum),
            base_currency=sampled_from([CurrencyEnum.USD]),
            quote_currency=sampled_from([CurrencyEnum.CHF]),
            forex_currency_pair=sampled_from([ForexPairEnum.USDCHF]),
            position=sampled_from(PositionEnum),
        )
    )
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_close_event_handler_for_bullish_event_for_base_currency(
        self, get_db, trade: Trade
    ):
        event = CloseTradeEvent(
            currency=CurrencyEnum.USD, sentiment=SentimentEnum.BULLISH
        )

        uow = MongoUnitOfWork(MockTradeConnect(), scraper=mock.MagicMock())
        async with uow:
            await uow.trade_repository.save(trade)
            await close_trade_handler(event, uow)
            closed_trade: TradeDomain = (
                await uow.trade_repository.get_trade_by_trade_id(
                    trade.trade_id
                )
            )
            assert closed_trade.position == PositionEnum.CLOSED

    @pytest.mark.asyncio
    @given(
        builds(
            Trade,
            trade_id=integers(min_value=12),
            position_size=integers(),
            stop=floats(),
            limit=floats(),
            is_buy=sampled_from([True]),
            signal=sampled_from(SignalTypeEnum),
            base_currency=sampled_from([CurrencyEnum.USD]),
            quote_currency=sampled_from([CurrencyEnum.CHF]),
            forex_currency_pair=sampled_from([ForexPairEnum.USDCHF]),
            position=sampled_from(PositionEnum),
        )
    )
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_close_event_handler_for_bearish_event_for_base_currency(
        self, get_db, trade: Trade
    ):
        event = CloseTradeEvent(
            currency=CurrencyEnum.USD, sentiment=SentimentEnum.BEARISH
        )

        uow = MongoUnitOfWork(
            MockTradeConnect(),
            scraper=mock.MagicMock(),
        )
        async with uow:
            await uow.trade_repository.save(trade)
            await close_trade_handler(event, uow)
            closed_trade: TradeDomain = (
                await uow.trade_repository.get_trade_by_trade_id(
                    trade.trade_id
                )
            )
            assert closed_trade.position == PositionEnum.CLOSED

    @pytest.mark.asyncio
    @given(
        builds(
            Trade,
            trade_id=integers(min_value=12),
            position_size=integers(),
            stop=floats(),
            limit=floats(),
            is_buy=sampled_from([True]),
            signal=sampled_from(SignalTypeEnum),
            base_currency=sampled_from([CurrencyEnum.GBP]),
            quote_currency=sampled_from([CurrencyEnum.USD]),
            forex_currency_pair=sampled_from([ForexPairEnum.GBPUSD]),
            position=sampled_from(PositionEnum),
        )
    )
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_close_event_handler_for_bullish_event_for_quoted_currency(
        self, get_db, trade: Trade
    ):
        event = CloseTradeEvent(
            currency=CurrencyEnum.USD, sentiment=SentimentEnum.BULLISH
        )

        uow = MongoUnitOfWork(
            MockTradeConnect(),
            scraper=mock.MagicMock(),
        )
        async with uow:
            await uow.trade_repository.save(trade)
            await close_trade_handler(event, uow)
            closed_trade: TradeDomain = (
                await uow.trade_repository.get_trade_by_trade_id(
                    trade.trade_id
                )
            )
            assert closed_trade.position == PositionEnum.CLOSED

    @pytest.mark.asyncio
    @given(
        builds(
            Trade,
            trade_id=integers(min_value=12),
            position_size=integers(),
            stop=floats(),
            limit=floats(),
            is_buy=sampled_from([False]),
            signal=sampled_from(SignalTypeEnum),
            base_currency=sampled_from([CurrencyEnum.GBP]),
            quote_currency=sampled_from([CurrencyEnum.USD]),
            forex_currency_pair=sampled_from([ForexPairEnum.GBPUSD]),
            position=sampled_from(PositionEnum),
        )
    )
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_close_event_handler_for_bearish_event_for_quoted_currency(
        self, get_db, trade: Trade
    ):
        event = CloseTradeEvent(
            currency=CurrencyEnum.USD, sentiment=SentimentEnum.BEARISH
        )

        uow = MongoUnitOfWork(
            MockTradeConnect(),
            scraper=mock.MagicMock(),
        )
        async with uow:
            await uow.trade_repository.save(trade)
            await close_trade_handler(event, uow)
            closed_trade: TradeDomain = (
                await uow.trade_repository.get_trade_by_trade_id(
                    trade.trade_id
                )
            )
            assert closed_trade.position == PositionEnum.CLOSED
