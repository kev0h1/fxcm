from datetime import datetime
from typing import Iterator
from src.domain.fundamental import FundamentalData
from src.config import CurrencyEnum, SentimentEnum
from typing import Iterator
from src.service_layer.uow import MongoUnitOfWork


class FundamentalDataService:
    def __init__(self, uow: MongoUnitOfWork) -> None:
        self._uow: MongoUnitOfWork = uow

    async def get_all_fundamental_data(
        self, **kwargs
    ) -> Iterator[FundamentalData]:
        """Get the fundamental data"""
        return await self._uow.fundamental_data_repository.get_all(**kwargs)

    async def get_fundamental_data_by_currency_datetime(
        self, currency: CurrencyEnum, last_updated: datetime
    ) -> FundamentalData:
        """Get the fundamental data for a currency"""
        return (
            await self._uow.fundamental_data_repository.get_fundamental_data(
                currency=currency, last_updated=last_updated
            )
        )

    async def create_fundamental_data(
        self, fundamental_data: FundamentalData
    ) -> FundamentalData:
        """Create a fundamental data object"""
        return await self._uow.fundamental_data_repository.save(
            fundamental_data=fundamental_data
        )

    async def get_latest_fundamental_data_for_currency(
        self, currency: CurrencyEnum
    ):
        """Return the latest data for a particular currency"""
        return await self._uow.fundamental_data_repository.get_latest_fundamental_data(
            currency=currency
        )

    async def calculate_aggregate_score(
        self, fundamental_data: FundamentalData
    ):
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
