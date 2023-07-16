from __future__ import annotations
import mock
from src.config import (
    PositionEnum,
    SignalTypeEnum,
    ForexPairEnum,
    CurrencyEnum,
)

from hypothesis.strategies import (
    from_type,
    builds,
    integers,
    floats,
    booleans,
    sampled_from,
)
from hypothesis import given, settings, HealthCheck
from src.adapters.database.repositories.trade_repository import TradeRepository

import pytest

from src.domain.trade import Trade
from src.adapters.fxcm_connect.mock_trade_connect import MockTradeConnect

from src.service_layer.uow import MongoUnitOfWork


class TestTradeOrm:
    @pytest.mark.asyncio
    @given(
        builds(
            Trade,
            trade_id=integers(),
            position_size=integers(),
            stop=floats(),
            limit=floats(),
            is_buy=booleans(),
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
    async def test_add_trade_to_db(self, get_db, trade: Trade):
        """Test adding a trade to the db"""
        uow = MongoUnitOfWork(
            fxcm_connection=MockTradeConnect(),
            scraper=mock.MagicMock(),
            db_name=get_db,
        )
        repo = TradeRepository()
        trade_id = trade.trade_id
        async with uow:
            await repo.save(trade)

        async with uow:
            trades = await repo.get_all()
            assert len(trades) > 0
            trade = await repo.get_trade_by_trade_id(trade_id=trade_id)
            assert trade is not None
