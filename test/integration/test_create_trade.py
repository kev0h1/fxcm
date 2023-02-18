from src.config import SignalTypeEnum
from src.models.db_connect import Database
from src.classes.trade import Trade
from hypothesis.strategies import (
    from_type,
    builds,
    integers,
    floats,
    booleans,
    sampled_from,
)
from hypothesis import given, settings, HealthCheck
from src.models.db_connect import context
from src.repositories.trade_repository import TradeRepository


class TestTradeOrm:
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
    def test_add_trade_to_db(self, get_db, trade):
        """Test adding a trade to the db"""
        repo = TradeRepository()
        trade_id = trade.trade_id
        with get_db.get_session():
            repo.add(trade)

        with get_db.get_session():
            trades = repo.get_all()
            assert len(trades) > 0
            trade = repo.get_trade_by_trade_id(trade_id=trade_id)
            assert trade is not None
