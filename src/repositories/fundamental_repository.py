import datetime
from typing import Iterator
from src.classes.fundamental import FundamentalData
from src.config import CurrencyEnum
from src.repositories.base_repository import BaseRepository


class FundamentalDataRepository(BaseRepository):
    def get_all(self) -> Iterator[FundamentalData]:
        return FundamentalData.objects()

    def get_fundamental_data(
        self, currency: CurrencyEnum, last_updated: datetime
    ) -> FundamentalData:
        return FundamentalData.objects(
            currency=currency, last_updated=last_updated
        )
