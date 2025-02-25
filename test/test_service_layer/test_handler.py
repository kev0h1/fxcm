from uuid import uuid4
from hypothesis import settings, given, HealthCheck
import mock
from src.adapters.database.mongo.trade_model import Trade
from src.adapters.fxcm_connect.mock_trade_connect import MockTradeConnect
from src.domain.events import (
    CloseForexPairEvent,
    CloseTradeEvent,
    OpenTradeEvent,
)
from src.domain.fundamental import FundamentalData
from src.service_layer.handlers import (
    close_forex_pair_handler,
    close_trade_handler,
    get_trade_parameters,
    open_trade_handler,
    get_combined_techincal_and_fundamental_sentiment,
)
from src.adapters.fxcm_connect.oanda_connect import OandaConnect
from src.config import (
    CurrencyEnum,
    ForexPairEnum,
    PositionEnum,
    SentimentEnum,
)
import pytest
from src.domain.trade import Trade as TradeDomain
from hypothesis.strategies import (
    builds,
    floats,
    sampled_from,
    lists,
    datetimes,
    text,
    booleans,
)
from datetime import datetime, timedelta

from src.service_layer.uow import MongoUnitOfWork
import mock


class TestCloseEventHandler:
    @pytest.mark.asyncio
    @given(
        builds(
            Trade,
            trade_id=text(),
            units=floats(),
            stop=floats(),
            limit=floats(),
            is_buy=sampled_from([False]),
            base_currency=sampled_from([CurrencyEnum.USD]),
            quote_currency=sampled_from([CurrencyEnum.CHF]),
            forex_currency_pair=sampled_from([ForexPairEnum.USDCHF]),
            position=sampled_from(PositionEnum),
            close=floats(),
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

        uow = MongoUnitOfWork(
            MockTradeConnect(),
            scraper=mock.MagicMock(),
            db_name=get_db,
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
            trade_id=text(),
            units=floats(),
            stop=floats(),
            limit=floats(),
            is_buy=sampled_from([True]),
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
            db_name=get_db,
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
            trade_id=text(),
            units=floats(),
            stop=floats(),
            limit=floats(),
            is_buy=sampled_from([True]),
            base_currency=sampled_from([CurrencyEnum.GBP]),
            quote_currency=sampled_from([CurrencyEnum.USD]),
            forex_currency_pair=sampled_from([ForexPairEnum.GBPUSD]),
            position=sampled_from(PositionEnum),
            close=floats(),
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
            db_name=get_db,
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
            trade_id=text(),
            units=floats(),
            stop=floats(),
            limit=floats(),
            is_buy=sampled_from([False]),
            base_currency=sampled_from([CurrencyEnum.GBP]),
            quote_currency=sampled_from([CurrencyEnum.USD]),
            forex_currency_pair=sampled_from([ForexPairEnum.GBPUSD]),
            position=sampled_from(PositionEnum),
            close=floats(),
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
            db_name=get_db,
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


class TestGetCombinedTechnicalAndFundamentalSentiment:
    @pytest.mark.asyncio
    @given(
        lists(
            builds(
                FundamentalData,
                currency=sampled_from(CurrencyEnum),
                last_updated=datetimes(),
            ),
            min_size=2,
            max_size=2,
        )
    )
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    @pytest.mark.parametrize(
        "base_sentiment, quoted_sentiment, event_sentiment, delay_quoted, expected, processed",
        [
            (
                SentimentEnum.BULLISH,
                SentimentEnum.BULLISH,
                SentimentEnum.BULLISH,
                True,
                SentimentEnum.FLAT,
                False,
            ),
            (
                SentimentEnum.BULLISH,
                SentimentEnum.BULLISH,
                SentimentEnum.BULLISH,
                True,
                SentimentEnum.BULLISH,
                True,
            ),
            (
                SentimentEnum.BULLISH,
                SentimentEnum.BULLISH,
                SentimentEnum.BULLISH,
                False,
                SentimentEnum.FLAT,
                True,
            ),
            (
                SentimentEnum.BULLISH,
                SentimentEnum.BEARISH,
                SentimentEnum.BULLISH,
                False,
                SentimentEnum.BULLISH,
                True,
            ),
            (
                SentimentEnum.BEARISH,
                SentimentEnum.BEARISH,
                SentimentEnum.BEARISH,
                True,
                SentimentEnum.BEARISH,
                True,
            ),
            (
                SentimentEnum.BEARISH,
                SentimentEnum.BULLISH,
                SentimentEnum.BEARISH,
                False,
                SentimentEnum.BEARISH,
                True,
            ),
            (
                SentimentEnum.BEARISH,
                SentimentEnum.BEARISH,
                SentimentEnum.BEARISH,
                False,
                SentimentEnum.FLAT,
                True,
            ),
            (
                SentimentEnum.BULLISH,
                SentimentEnum.BULLISH,
                SentimentEnum.BEARISH,
                True,
                SentimentEnum.FLAT,
                True,
            ),
            (
                SentimentEnum.BEARISH,
                SentimentEnum.BULLISH,
                SentimentEnum.BULLISH,
                True,
                SentimentEnum.FLAT,
                True,
            ),
        ],
        ids=[
            "test_when_sentiment_is_bullish_and_base_latest_and_not_processed",
            "test_when_sentiment_is_bullish_and_base_latest",
            "test_when_sentiment_is_bullish_but_quoted_is_latest_and_bullish",
            "test_when_sentiment_is_bullish_but_quoted_is_latest_and_bearish",
            "test_when_sentiment_is_bearish_and_base_latest",
            "test_when_sentiment_is_bearish_and_quoted_is_latest_and_bullish",
            "test_when_sentiment_is_bearish_and_quoted_is_latest_and_bearish",
            "test_when_base_is_bullish_and_event_is_bearish",
            "test_when_base_is_bearish_and_event_is_bullish",
        ],
    )
    async def test_get_combined_techincal_and_fundamental_sentiment(
        self,
        base_sentiment,
        quoted_sentiment,
        event_sentiment,
        delay_quoted,
        expected,
        processed,
        get_db,
        fundamentals: list[FundamentalData],
    ):
        uow = MongoUnitOfWork(
            MockTradeConnect(),
            scraper=mock.MagicMock(),
            db_name=get_db,
        )

        async with uow:
            for index, fundamental in enumerate(fundamentals):
                if index == 0:
                    fundamental.currency = CurrencyEnum.USD
                    fundamental.aggregate_sentiment = base_sentiment
                    fundamental.processed = processed
                    fundamental.last_updated = (
                        datetime.now()
                        if delay_quoted
                        else datetime.now() - timedelta(minutes=1)
                    )

                else:
                    fundamental.currency = CurrencyEnum.CAD
                    fundamental.processed = processed
                    fundamental.aggregate_sentiment = quoted_sentiment
                    fundamental.last_updated = (
                        datetime.now() - timedelta(minutes=1)
                        if delay_quoted
                        else datetime.now()
                    )
                await uow.fundamental_data_repository.save(fundamental)

        event = OpenTradeEvent(
            forex_pair=ForexPairEnum.USDCAD,
            sentiment=event_sentiment,
            stop=1.3,
            close=1.2,
        )

        async with uow:
            combined_sentiment = (
                await get_combined_techincal_and_fundamental_sentiment(
                    event, uow, ForexPairEnum.USDCAD.value.split("/")
                )
            )

            assert combined_sentiment == expected

    @pytest.mark.asyncio
    @given(
        lists(
            builds(
                FundamentalData,
                currency=sampled_from(CurrencyEnum),
                last_updated=datetimes(),
            ),
            min_size=2,
            max_size=2,
        )
    )
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    @pytest.mark.parametrize(
        "base_sentiment, quoted_sentiment, event_sentiment, delay_quoted, expected, processed",
        [
            (
                SentimentEnum.BULLISH,
                SentimentEnum.BULLISH,
                SentimentEnum.BULLISH,
                True,
                SentimentEnum.FLAT,
                True,
            ),
        ],
        ids=[
            "test_when_spread_is_high",
        ],
    )
    async def test_get_when_spread_is_high(
        self,
        base_sentiment,
        quoted_sentiment,
        event_sentiment,
        delay_quoted,
        expected,
        processed,
        get_db,
        fundamentals: list[FundamentalData],
    ):
        uow = MongoUnitOfWork(
            MockTradeConnect(),
            scraper=mock.MagicMock(),
            db_name=get_db,
        )
        with mock.patch.object(MockTradeConnect, "get_spread") as mock_spread:
            mock_spread.return_value = 13
            async with uow:
                for index, fundamental in enumerate(fundamentals):
                    if index == 0:
                        fundamental.currency = CurrencyEnum.USD
                        fundamental.aggregate_sentiment = base_sentiment
                        fundamental.processed = processed
                        fundamental.last_updated = (
                            datetime.now()
                            if delay_quoted
                            else datetime.now() - timedelta(minutes=1)
                        )

                    else:
                        fundamental.currency = CurrencyEnum.CAD
                        fundamental.processed = processed
                        fundamental.aggregate_sentiment = quoted_sentiment
                        fundamental.last_updated = (
                            datetime.now() - timedelta(minutes=1)
                            if delay_quoted
                            else datetime.now()
                        )
                    await uow.fundamental_data_repository.save(fundamental)

            event = OpenTradeEvent(
                forex_pair=ForexPairEnum.USDCAD,
                sentiment=event_sentiment,
                stop=1.3,
                close=1.2,
            )

            async with uow:
                combined_sentiment = (
                    await get_combined_techincal_and_fundamental_sentiment(
                        event, uow, ForexPairEnum.USDCAD.value.split("/")
                    )
                )

                assert combined_sentiment == expected


class TestOpenTradeHandler:
    @pytest.mark.asyncio
    @given(
        lists(
            builds(
                FundamentalData,
                currency=sampled_from(CurrencyEnum),
                last_updated=datetimes(),
            ),
            min_size=2,
            max_size=2,
        )
    )
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    @pytest.mark.parametrize(
        "base_sentiment, quoted_sentiment, event_sentiment, delay_quoted, expected",
        [
            (
                SentimentEnum.BULLISH,
                SentimentEnum.BULLISH,
                SentimentEnum.BULLISH,
                True,
                1,
            ),
            (
                SentimentEnum.BEARISH,
                SentimentEnum.BEARISH,
                SentimentEnum.BEARISH,
                True,
                1,
            ),
        ],
        ids=[
            "test_when_sentiment_is_bullish",
            "test_when_sentiment_is_bearish",
        ],
    )
    async def test_open_trade_handler(
        self,
        base_sentiment,
        quoted_sentiment,
        event_sentiment,
        delay_quoted,
        expected,
        get_db,
        fundamentals: list[FundamentalData],
    ):
        uow = MongoUnitOfWork(
            MockTradeConnect(),
            scraper=mock.MagicMock(),
            db_name=get_db,
        )

        event = OpenTradeEvent(
            forex_pair=ForexPairEnum.USDCAD,
            sentiment=event_sentiment,
            stop=1.3,
            close=1.2,
            limit=None,
        )

        async with uow:
            for index, fundamental in enumerate(fundamentals):
                if index == 0:
                    fundamental.currency = CurrencyEnum.USD
                    fundamental.aggregate_sentiment = base_sentiment
                    fundamental.processed = True
                    fundamental.last_updated = (
                        datetime.now()
                        if delay_quoted
                        else datetime.now() - timedelta(minutes=1)
                    )

                else:
                    fundamental.currency = CurrencyEnum.CAD
                    fundamental.aggregate_sentiment = quoted_sentiment
                    fundamental.processed = True
                    fundamental.last_updated = (
                        datetime.now() - timedelta(minutes=1)
                        if delay_quoted
                        else datetime.now()
                    )
                await uow.fundamental_data_repository.save(fundamental)
            await open_trade_handler(event, uow)
            trades = await uow.trade_repository.get_all()
            assert len(trades) == expected

    class TestGetTradeParameters:
        @pytest.mark.asyncio
        @pytest.mark.parametrize(
            "sentiment, expected, units, stop, close, forex_pair, exchange_rate",
            [
                (
                    SentimentEnum.BULLISH,
                    True,
                    int(
                        10000
                        * (100000 * 0.02)
                        / (
                            (
                                abs(0.8784 - 0.8804)
                                / 0.0001
                                * 100000
                                * 0.0001
                                * (1 / 1.72556)
                            )
                        )
                    ),
                    0.8784,
                    0.8804,
                    ForexPairEnum.USDCAD,
                    1.72556,
                ),
                (
                    SentimentEnum.BEARISH,
                    False,
                    int(
                        10000
                        * (100000 * 0.02)
                        / (
                            (
                                abs(145.748 - 145.81)
                                / 0.01
                                * 100000
                                * 0.01
                                * (1 / 185.967)
                            )
                        )
                    ),
                    145.81,
                    145.748,
                    ForexPairEnum.USDJPY,
                    185.967,
                ),
            ],
        )
        async def test_get_trade_parameters(
            self,
            sentiment,
            expected,
            stop,
            close,
            forex_pair,
            exchange_rate,
            get_db,
            units,
        ):
            with mock.patch.object(
                MockTradeConnect, "get_latest_close"
            ) as mock_get_exchange_rate:
                mock_get_exchange_rate.return_value = exchange_rate

                uow = MongoUnitOfWork(
                    MockTradeConnect(),
                    scraper=mock.MagicMock(),
                    db_name=get_db,
                )
                event = OpenTradeEvent(
                    forex_pair=forex_pair,
                    sentiment=sentiment,
                    stop=stop,
                    close=close,
                    limit=None,
                )

                (
                    is_buy,
                    amount,
                    stop_loss,
                    sl_pips,
                    limit,
                ) = await get_trade_parameters(
                    event, uow, forex_pair.value.split("/")
                )
                assert is_buy == expected
                assert amount == units
                # assert stop_loss == 1.3

    class TestCloseForexPairHandler:
        @pytest.mark.asyncio
        @pytest.mark.parametrize(
            "sentiment", [SentimentEnum.BULLISH, SentimentEnum.BEARISH]
        )
        @given(
            lists(
                builds(
                    Trade,
                    trade_id=text(min_size=1, max_size=10),
                    units=floats(),
                    stop=floats(),
                    limit=floats(),
                    is_buy=booleans(),
                    base_currency=sampled_from([CurrencyEnum.USD]),
                    quote_currency=sampled_from([CurrencyEnum.CHF]),
                    forex_currency_pair=sampled_from([ForexPairEnum.USDCHF]),
                    position=sampled_from([PositionEnum.OPEN]),
                    close=floats(),
                ),
                min_size=2,
                max_size=2,
            ),
        )
        @settings(
            max_examples=1,
            suppress_health_check=[HealthCheck.function_scoped_fixture],
            deadline=None,
        )
        async def test_close_forex_pair_handler(
            self, sentiment, get_db, trades
        ):
            uow = MongoUnitOfWork(
                MockTradeConnect(),
                scraper=mock.MagicMock(),
                db_name=get_db,
            )
            async with uow:
                for trade in trades:
                    trade.is_buy = (
                        True if sentiment == SentimentEnum.BULLISH else False
                    )
                    trade.id = str(uuid4())
                    await uow.trade_repository.save(trade)

            event = CloseForexPairEvent(
                forex_pair=ForexPairEnum.USDCHF, sentiment=sentiment
            )
            async with uow:
                trade_repos = await uow.trade_repository.get_open_trades()
                assert len(trade_repos) == len(trades)
                await close_forex_pair_handler(event, uow)

            async with uow:
                trade_repos = await uow.trade_repository.get_open_trades()
                assert len(trade_repos) == 0
