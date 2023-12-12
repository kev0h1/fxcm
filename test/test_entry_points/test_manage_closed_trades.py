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
from src.entry_points.scheduler.manage_closed_trades import (
    manage_closed_trades,
)


class TestManageClosedTrades:
    @pytest.mark.asyncio
    @given(
        builds(
            Trade,
            trade_id=text(min_size=2),
            units=floats(),
            stop=floats(),
            limit=floats(),
            is_buy=sampled_from([True]),
            base_currency=sampled_from([CurrencyEnum.USD]),
            quote_currency=sampled_from([CurrencyEnum.CHF]),
            forex_currency_pair=sampled_from([ForexPairEnum.USDCHF]),
            position=sampled_from([PositionEnum.OPEN]),
            close=floats(),
        )
    )
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    async def test_manage_closed_trades(self, get_db, trade: Trade):
        uow = MongoUnitOfWork(
            fxcm_connection=MockTradeConnect(),
            scraper=mock.MagicMock(),
            sentiment_scraper=mock.MagicMock(),
            db_name=get_db,
        )

        with mock.patch.object(uow.fxcm_connection, "get_trade_state") as mock_method:
            async with uow:
                await uow.trade_repository.save(trade)
            mock_method.return_value = ("OPEN", 0)

            await manage_closed_trades(uow=uow)

            async with uow:
                trades = await uow.trade_repository.get_all()
                trades[0].position = PositionEnum.OPEN

            mock_method.return_value = "CLOSED", 2000
            await manage_closed_trades(uow=uow)

            async with uow:
                trades = await uow.trade_repository.get_all()
                trades[0].position = PositionEnum.CLOSED
                trades[0].is_winner = True
