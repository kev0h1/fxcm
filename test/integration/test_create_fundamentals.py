import mock
from src.adapters.fxcm_connect.mock_trade_connect import MockTradeConnect
from src.config import CurrencyEnum
from src.adapters.database.mongo.fundamental_models import FundamentalData
from hypothesis.strategies import (
    builds,
    datetimes,
    sampled_from,
    lists,
    integers,
    just,
)
from datetime import datetime, timedelta
from hypothesis import given, settings, HealthCheck

import pytest

from src.service_layer.uow import MongoUnitOfWork

import random


def get_unique_datetime() -> datetime:
    return datetime.now() + timedelta(days=random.randint(-100, 100))


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
            fxcm_connection=MockTradeConnect(),
            scraper=mock.MagicMock(),
            db_name=get_db,
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

    @pytest.mark.asyncio
    @given(
        lists(
            builds(
                FundamentalData,
                currency=sampled_from(CurrencyEnum),
                last_updated=datetimes(),
            ),
            min_size=3,
        )
    )
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    async def test_get_fundamental_data(self, get_db, fundamentals):
        uow = MongoUnitOfWork(
            fxcm_connection=MockTradeConnect(),
            scraper=mock.MagicMock(),
            db_name=get_db,
        )
        async with uow:
            for fundamental in fundamentals:
                await uow.fundamental_data_repository.save(fundamental)
        async with uow:
            objs = await uow.fundamental_data_repository.get_all()
            assert len(objs) > 0
        async with uow:
            fundamental_data = (
                await uow.fundamental_data_repository.get_fundamental_data(
                    fundamentals[0].currency, fundamentals[0].last_updated
                )
            )
            assert fundamental_data is not None

    @pytest.mark.asyncio
    @given(
        lists(
            builds(
                FundamentalData,
                currency=sampled_from([CurrencyEnum.USD]),
                processed=just(True),
                last_updated=datetimes(),
            ),
            min_size=3,
            max_size=3,
        )
    )
    @settings(
        max_examples=1,
        suppress_health_check=[HealthCheck.function_scoped_fixture],
        deadline=None,
    )
    async def test_get_latest_fundamental_data(self, get_db, fundamentals):
        uow = MongoUnitOfWork(
            fxcm_connection=MockTradeConnect(),
            scraper=mock.MagicMock(),
            db_name=get_db,
        )
        async with uow:
            for fundamental in fundamentals:
                fundamental.last_updated = get_unique_datetime()
                await uow.fundamental_data_repository.save(fundamental)
        async with uow:
            objs = await uow.fundamental_data_repository.get_all()
            assert len(objs) > 0

        max_object = max(objs, key=lambda x: x.last_updated)
        async with uow:
            fundamental_data = await uow.fundamental_data_repository.get_latest_fundamental_data(
                CurrencyEnum.USD
            )
            assert fundamental_data == max_object
