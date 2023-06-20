import mock
from src.config import SignalTypeEnum
from src.adapters.database.sql.db_connect import Database
from src.adapters.database.mongo.trade_model import Trade
from hypothesis.strategies import (
    from_type,
    builds,
    integers,
    floats,
    booleans,
    sampled_from,
)
from hypothesis import given, settings, HealthCheck
from src.adapters.database.sql.db_connect import context
from src.adapters.database.repositories.trade_repository import TradeRepository

import pytest

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
        )
    )
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
    )
    async def test_add_trade_to_db(self, get_db, trade):
        """Test adding a trade to the db"""
        uow = MongoUnitOfWork(event_bus=mock.MagicMock())
        repo = TradeRepository()
        trade_id = trade.trade_id
        async with uow:
            await repo.save(trade)

        async with uow:
            trades = await repo.get_all()
            assert len(trades) > 0
            trade = await repo.get_trade_by_trade_id(trade_id=trade_id)
            assert trade is not None
