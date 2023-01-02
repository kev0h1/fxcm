from src.models.db_connect import DbSession
from src.classes.trade import Trade
from hypothesis.strategies import from_type
from hypothesis import given, settings


class TestTradeOrm:
    @given(from_type(Trade))
    @settings(max_examples=1)
    def test_add_trade_to_db(self, trade):
        """Test adding a trade to the db"""
        trade_id = trade.trade_id
        with DbSession.session.begin() as session:
            session.add(trade)

        with DbSession.session.begin() as session:
            trades = Trade.get_trades(session=session)
            assert len(trades) > 0
            trade = Trade.get_trade_by_trade_id(
                session=session, trade_id=trade_id
            )
            assert trade is not None
