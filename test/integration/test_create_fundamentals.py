import mock
from src.adapters.fxcm_connect.mock_trade_connect import MockTradeConnect
from src.config import CurrencyEnum, SentimentEnum
from src.adapters.database.mongo.fundamental_models import FundamentalData
from hypothesis.strategies import builds, datetimes, floats, sampled_from, text
from hypothesis import given, settings, HealthCheck

import pytest

from src.service_layer.uow import MongoUnitOfWork


class TestFundamentalMapper:
    @pytest.mark.asyncio
    @given(
        builds(
            FundamentalData,
            currency=sampled_from(CurrencyEnum),
            last_updated=datetimes(),
        )
    )
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    async def test_add_fundamental_data_to_db(
        self, get_db, data: FundamentalData
    ):
        uow = MongoUnitOfWork(
            event_bus=mock.MagicMock(),
            fxcm_connection=MockTradeConnect(),
            scraper=mock.MagicMock(),
        )
        currency = data.currency
        last_updated = data.last_updated
        async with uow:
            await uow.fundamental_data_repository.save(data)
        async with uow:
            objs = await uow.fundamental_data_repository.get_all()
            assert len(objs) > 0
        async with uow:
            fundamental_data = (
                await uow.fundamental_data_repository.get_fundamental_data(
                    currency, last_updated
                )
            )
            assert fundamental_data is not None
