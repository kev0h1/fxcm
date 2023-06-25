import datetime
from typing import Iterator
from src.adapters.database.mongo.fundamental_models import FundamentalData
from src.domain.fundamental import FundamentalData as FundamentalDataDomain
from src.config import CurrencyEnum
from src.adapters.database.mongo.fundamental_models import (
    map_to_db_model,
    map_to_domain_model,
)


class FundamentalDataRepository:
    async def save(self, obj: FundamentalDataDomain):
        """Add an object"""
        model = await map_to_db_model(fundamental_data=obj)
        model.save()
        return obj

    async def get_all(self, **kwargs) -> Iterator[FundamentalDataDomain]:
        date = None
        if "last_updated" in kwargs:
            date = kwargs.pop("last_updated")
            next_day = date + datetime.timedelta(days=1)
        objs = FundamentalData.objects(**kwargs)
        if date:
            return [
                await map_to_domain_model(obj)
                for obj in objs.filter(
                    last_updated__gte=date, last_updated__lte=next_day
                )
            ]
        return [await map_to_domain_model(obj) for obj in objs]

    async def get_fundamental_data(
        self, currency: CurrencyEnum, last_updated: datetime
    ) -> FundamentalDataDomain:
        return await map_to_domain_model(
            FundamentalData.objects(
                currency=currency, last_updated=last_updated
            ).first()
        )

    async def get_latest_fundamental_data(
        self, currency: CurrencyEnum
    ) -> FundamentalDataDomain:
        """Gets the latest fundamental data for a currency"""
        return await map_to_domain_model(
            (
                FundamentalData.objects(
                    currency=currency,
                )
                .order_by("-last_updated")
                .first()
            )
        )
