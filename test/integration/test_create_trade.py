from src.config import SignalTypeEnum
from src.adapters.database.sql.db_connect import Database
from src.domain.trade import Trade
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
        repo = TradeRepository()
        trade_id = trade.trade_id
        with get_db.get_session():
            await repo.save(trade)

        with get_db.get_session():
            trades = await repo.get_all()
            assert len(trades) > 0
            trade = await repo.get_trade_by_trade_id(trade_id=trade_id)
            assert trade is not None
