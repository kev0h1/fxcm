from datetime import datetime
from typing import Iterator
from src.domain.fundamental import FundamentalData
from src.config import CurrencyEnum, SentimentEnum

from src.adapters.database.repositories.fundamental_repository import (
    FundamentalDataRepository,
)
from contextlib import AbstractContextManager
from typing import Callable, Iterator
from sqlalchemy.orm import Session
from src.adapters.database.sql.db_connect import context


class FundamentalDataService:
    def __init__(
        self, fundamental_data_repository: FundamentalDataRepository
    ) -> None:
        self._repository: FundamentalDataRepository = (
            fundamental_data_repository
        )

    async def get_all_fundamental_data(
        self, **kwargs
    ) -> Iterator[FundamentalData]:
        """Get the fundamental data"""
        return self._repository.get_all(**kwargs)

    def get_fundamental_data_by_currency_datetime(
        self, currency: CurrencyEnum, last_updated: datetime
    ) -> FundamentalData:
        """Get the fundamental data for a currency"""
        return self._repository.get_fundamental_data(
            currency=currency, last_updated=last_updated
        )

    def create_fundamental_data(
        self, fundamental_data: FundamentalData
    ) -> FundamentalData:
        """Create a fundamental data object"""
        return self._repository.save(fundamental_data=fundamental_data)

    def get_latest_fundamental_data_for_currency(self, currency: CurrencyEnum):
        """Return the latest data for a particular currency"""
        return self._repository.get_latest_fundamental_data(currency=currency)

    def calculate_aggregate_score(self, fundamental_data: FundamentalData):
        """Calculate the aggregate score of a fundmental data"""
        score = 0
        for calendar_event in fundamental_data.calendar_events:
            if calendar_event.sentiment == SentimentEnum.BULLISH:
                score += 1
            elif calendar_event.sentiment == SentimentEnum.BEARISH:
                score -= 1

        if score > 0:
            fundamental_data.aggregate_sentiment = SentimentEnum.BULLISH
        elif score < 0:
            fundamental_data.aggregate_sentiment = SentimentEnum.BEARISH
        else:
            fundamental_data.aggregate_sentiment = SentimentEnum.FLAT
