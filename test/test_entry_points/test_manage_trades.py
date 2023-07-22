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
from src.entry_points.scheduler.manage_trades import manage_trades


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
            close=sampled_from([1.6520]),
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
            mock_method.return_value = 1.6535
            async with uow:
                await uow.trade_repository.save(trade)
            await manage_trades(uow=uow)

            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - 1.652) < 0.0001

            mock_method.return_value = 1.6536
            await manage_trades(uow=uow)
            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - 1.6521) < 0.0001

            mock_method.return_value = 1.6538
            await manage_trades(uow=uow)
            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - 1.6523) < 0.0001

    @pytest.mark.asyncio
    @given(
        builds(
            Trade,
            trade_id=text(min_size=2),
            units=floats(),
            stop=sampled_from([1.6530]),
            limit=floats(),
            is_buy=sampled_from([False]),
            base_currency=sampled_from([CurrencyEnum.USD]),
            quote_currency=sampled_from([CurrencyEnum.CHF]),
            forex_currency_pair=sampled_from([ForexPairEnum.USDCHF]),
            position=sampled_from([PositionEnum.OPEN]),
            close=sampled_from([1.6520]),
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
            mock_method.return_value = 1.6505
            async with uow:
                await uow.trade_repository.save(trade)
            await manage_trades(uow=uow)

            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - 1.6520) < 0.0001

            mock_method.return_value = 1.6504
            await manage_trades(uow=uow)
            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - 1.6519) < 0.0001

            mock_method.return_value = 1.6502
            await manage_trades(uow=uow)
            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - 1.6517) < 0.0001
