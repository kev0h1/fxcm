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
from src.service_layer.indicators import Indicators
import pytest
import pandas as pd

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
            half_spread_cost=sampled_from([0.0001]),
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
        multiplier = 3
        close = 1.6520

        data_frame = pd.DataFrame(
            [
                {
                    "atr": 0.0001,
                    "close": close,
                }
            ]
        )

        with mock.patch.object(Indicators, "get_atr") as mock_method:
            mock_method.return_value = data_frame
            async with uow:
                await uow.trade_repository.save(trade)
            await manage_trades_handler(uow=uow, indicator=Indicators())

            expected_stop = (
                close - trade.half_spread_cost - multiplier * 0.0001
            )
            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - expected_stop) < 0.0001

            # price moves back down, expect the stop not to have changed
            mock_method.return_value = pd.DataFrame(
                [
                    {
                        "atr": 0.0001,
                        "close": 1.6518,
                    }
                ]
            )
            await manage_trades_handler(uow=uow, indicator=Indicators())
            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - expected_stop) < 0.0001

            close = 1.6525
            mock_method.return_value = pd.DataFrame(
                [
                    {
                        "atr": 0.0001,
                        "close": 1.6525,
                    }
                ]
            )
            await manage_trades_handler(uow=uow, indicator=Indicators())
            expected_stop = (
                close - trade.half_spread_cost - multiplier * 0.0001
            )
            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - expected_stop) < 0.0001

            mock_method.return_value = pd.DataFrame(
                [
                    {
                        "atr": 0.0001,
                        "close": 1.6517,
                    }
                ]
            )
            await manage_trades_handler(uow=uow, indicator=Indicators())
            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - expected_stop) < 0.0001
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
            close=sampled_from([1.6521]),
            sl_pips=sampled_from([9]),
            half_spread_cost=sampled_from([0.0001]),
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

        multiplier = 3
        close = 1.6516

        data_frame = pd.DataFrame(
            [
                {
                    "atr": 0.0001,
                    "close": close,
                }
            ]
        )

        with mock.patch.object(Indicators, "get_atr") as mock_method:
            mock_method.return_value = data_frame
            async with uow:
                await uow.trade_repository.save(trade)
            await manage_trades_handler(uow=uow, indicator=Indicators())

            expected_close = (
                close + trade.half_spread_cost + multiplier * 0.0001
            )
            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - expected_close) < 0.0001

            mock_method.return_value = pd.DataFrame(
                [
                    {
                        "atr": 0.0001,
                        "close": 1.6518,
                    }
                ]
            )
            await manage_trades_handler(uow=uow, indicator=Indicators())
            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - expected_close) < 0.0001

            close = 1.6510
            mock_method.return_value = pd.DataFrame(
                [
                    {
                        "atr": 0.0001,
                        "close": close,
                    }
                ]
            )
            await manage_trades_handler(uow=uow, indicator=Indicators())
            expected_close = (
                close + trade.half_spread_cost + multiplier * 0.0001
            )
            async with uow:
                trades = await uow.trade_repository.get_all()
                assert abs(trades[0].stop - expected_close) < 0.0001

            mock_method.return_value = mock_method.return_value = pd.DataFrame(
                [
                    {
                        "atr": 0.0001,
                        "close": 1.6520,
                    }
                ]
            )
            await manage_trades_handler(uow=uow, indicator=Indicators())
            async with uow:
                trades = await uow.trade_repository.get_open_trades()
                assert len(trades) == 0
