from datetime import datetime
from typing import Iterator
from src.classes.fundamental import FundamentalData
from src.config import CurrencyEnum

from src.repositories.fundamental_repository import FundamentalDataRepository


class FundamentalDataService:
    def __init__(
        self, fundamental_data_repository: FundamentalDataRepository
    ) -> None:
        self._repository: FundamentalDataRepository = (
            fundamental_data_repository
        )

    def get_all_fundamental_data(self) -> Iterator[FundamentalData]:
        return self._repository.get_all()

    def get_fundamental_data_by_currency_datetime(
        self, currency: CurrencyEnum, last_updated: datetime
    ) -> FundamentalData:
        return self._repository.get_fundamental_data(
            currency=currency, last_updated=last_updated
        )

    def create_fundamental_data(
        self, fundamental_data: FundamentalData
    ) -> FundamentalData:
        return self._repository.add(fundamental_data=fundamental_data)
