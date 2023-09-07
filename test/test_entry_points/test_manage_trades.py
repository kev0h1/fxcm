from hypothesis.strategies import (
    builds,
    text,
    floats,
    sampled_from,
)
from hypothesis import given, settings, HealthCheck
import mock
from src.adapters.fxcm_connect.mock_trade_connect import MockTradeConnect
from src.config import (
    PositionEnum,
    ForexPairEnum,
    CurrencyEnum,
)
import pytest

from src.domain.trade import Trade
from src.service_layer.uow import MongoUnitOfWork
from src.entry_points.scheduler.manage_trades import manage_trades_handler


class TestManageTrades:
    @pytest.mark.asyncio
    @given(
        builds(
            Trade,
            trade_id=text(min_size=2),
            units=floats(),
            stop=sampled_from([1.6510]),
            limit=floats(),
            is_buy=sampled_from([True]),
            base_currency=sampled_from([CurrencyEnum.USD]),
            quote_currency=sampled_from([CurrencyEnum.CHF]),
            forex_currency_pair=sampled_from([ForexPairEnum.USDCHF]),
            position=sampled_from([PositionEnum.OPEN]),
            close=sampled_from([1.6515]),
            sl_pips=sampled_from([5]),
        )
    )
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    async def test_manage_trades_for_buy(self, get_db, trade: Trade):
        uow = MongoUnitOfWork(
            fxcm_connection=MockTradeConnect(),
            scraper=mock.MagicMock(),
            db_name=get_db,
        )

        with mock.patch.object(
            uow.fxcm_connection, "get_latest_close"
        ) as mock_method:
            mock_method.return_value = 1.6520
            async with uow:
                await uow.trade_repository.save(trade)
            await manage_trades_handler(uow=uow)

            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - 1.6515) < 0.0001

            mock_method.return_value = 1.6521
            await manage_trades_handler(uow=uow)
            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - 1.6516) < 0.0001

            mock_method.return_value = 1.6523
            await manage_trades_handler(uow=uow)
            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - 1.6518) < 0.0001

            mock_method.return_value = 1.6516
            await manage_trades_handler(uow=uow)
            async with uow:
                trades = await uow.trade_repository.get_open_trades()
                assert len(trades) == 0

    @pytest.mark.asyncio
    @given(
        builds(
            Trade,
            trade_id=text(min_size=2),
            units=floats(),
            stop=sampled_from([1.6529]),
            limit=floats(),
            is_buy=sampled_from([False]),
            base_currency=sampled_from([CurrencyEnum.USD]),
            quote_currency=sampled_from([CurrencyEnum.CHF]),
            forex_currency_pair=sampled_from([ForexPairEnum.USDCHF]),
            position=sampled_from([PositionEnum.OPEN]),
            close=sampled_from([1.6520]),
            sl_pips=sampled_from([9]),
        )
    )
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    async def test_manage_trades_for_sell(self, get_db, trade: Trade):
        uow = MongoUnitOfWork(
            fxcm_connection=MockTradeConnect(),
            scraper=mock.MagicMock(),
            db_name=get_db,
        )

        with mock.patch.object(
            uow.fxcm_connection, "get_latest_close"
        ) as mock_method:
            mock_method.return_value = 1.6511
            async with uow:
                await uow.trade_repository.save(trade)
            await manage_trades_handler(uow=uow)

            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - 1.6516) < 0.0001

            mock_method.return_value = 1.6510
            await manage_trades_handler(uow=uow)
            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - 1.6515) < 0.0001

            mock_method.return_value = 1.6508
            await manage_trades_handler(uow=uow)
            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - 1.6513) < 0.0001

            mock_method.return_value = 1.6520
            await manage_trades_handler(uow=uow)
            async with uow:
                trades = await uow.trade_repository.get_open_trades()
                assert len(trades) == 0

    @pytest.mark.asyncio
    @given(
        builds(
            Trade,
            trade_id=text(min_size=2),
            units=floats(),
            stop=sampled_from([1.6515]),
            limit=floats(),
            is_buy=sampled_from([True]),
            base_currency=sampled_from([CurrencyEnum.USD]),
            quote_currency=sampled_from([CurrencyEnum.CHF]),
            forex_currency_pair=sampled_from([ForexPairEnum.USDCHF]),
            position=sampled_from([PositionEnum.OPEN]),
            close=sampled_from([1.6520]),
            sl_pips=sampled_from([5]),
        )
    )
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    async def test_manage_trades_for_buy_less_than_be_of_10(
        self, get_db, trade: Trade
    ):
        uow = MongoUnitOfWork(
            fxcm_connection=MockTradeConnect(),
            scraper=mock.MagicMock(),
            db_name=get_db,
        )

        with mock.patch.object(
            uow.fxcm_connection, "get_latest_close"
        ) as mock_method:
            mock_method.return_value = 1.6525
            async with uow:
                await uow.trade_repository.save(trade)
            await manage_trades_handler(uow=uow)

            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - 1.6520) < 0.0001

            mock_method.return_value = 1.6526
            await manage_trades_handler(uow=uow)
            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - 1.6521) < 0.0001

            mock_method.return_value = 1.6528
            await manage_trades_handler(uow=uow)
            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - 1.6523) < 0.0001
