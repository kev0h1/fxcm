from datetime import datetime
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.container.container import Container
from src.adapters.database.mongo.mongo_connect import Database

from src.adapters.database.repositories.fundamental_repository import (
    FundamentalDataRepository,
)
from src.service_layer.fundamental_service import FundamentalDataService

scheduler = AsyncIOScheduler()
from src.domain.fundamental import FundamentalData
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.config import CurrencyEnum

from src.service_layer.forex_factory_scraper import (
    CALENDAR_CURRENCY,
    ForexFactoryScraper,
)


@scheduler.scheduled_job("interval", seconds=300)
async def get_fundamental_trend_data():
    date_: datetime = datetime.today()
    # if date_.weekday
    if date_.weekday() < 5:
        url = ForexFactoryScraper.get_url_for_today(date_=date_)
        scraper = ForexFactoryScraper(url=url)
        objects = await scraper.get_fundamental_items()
        scraped_data = objects[-1]
        await process_data(scraper, objects, date_, scraped_data)


@inject
async def process_data(
    scraper: ForexFactoryScraper,
    objects,
    date_,
    scraped_data,
    fundamental_data_repository: FundamentalDataRepository = Depends(
        Provide[Container.fundamental_data_repository]
    ),
    db: Database = Depends(
        Provide[Container.db],
    ),
    fundamental_data_service: FundamentalDataService = Depends(
        Provide[Container.fundamental_data_service]
    ),
) -> List[FundamentalData]:
    """Converts the fundamental data into objects we can manipulate"""
    with db.get_session():
        for index, data in enumerate(scraped_data):
            time = await scraper.get_time_value(objects, -1, index)
            if time is None:
                continue
            date_time = datetime.combine(date_, time)
            currency = await scraper.get_event_values(
                element=data, class_name=CALENDAR_CURRENCY
            )
            if currency not in CurrencyEnum.__members__:
                continue
            currency = CurrencyEnum(currency)
            scraped_calendar_event = await scraper.create_calendar_event(
                tag=data
            )

            if scraped_calendar_event:
                fundamental_data = (
                    await fundamental_data_repository.get_fundamental_data(
                        currency=currency, last_updated=date_time
                    )
                )
                if not fundamental_data:
                    fundamental_data = await scraper.create_fundamental_object(
                        date_, data, time
                    )
                    fundamental_data = await fundamental_data_repository.save(
                        fundamental_data
                    )
                calender_event = (
                    await fundamental_data_repository.get_calendar_event(
                        fundamental_data=fundamental_data,
                        calendar_event=scraped_calendar_event.calendar_event,
                    )
                )
                if not calender_event:
                    fundamental_data.calendar_events.append(
                        scraped_calendar_event
                    )
                elif (
                    not calender_event.actual
                    or not calender_event.forecast
                    or not calender_event.previous
                ):
                    fundamental_data.actual = scraped_calendar_event.actual
                    fundamental_data.previous = scraped_calendar_event.previous
                    fundamental_data.forecast = scraped_calendar_event.forecast
                    fundamental_data.sentiment = (
                        scraped_calendar_event.sentiment
                    )
                await fundamental_data_service.calculate_aggregate_score(
                    fundamental_data=fundamental_data
                )
                await fundamental_data_repository.save(fundamental_data)


@inject
def check_for_trades(
    fundamental_data_repository: FundamentalDataRepository = Depends(
        Provide[Container.fundamental_data_repository]
    ),
):
    """Checks for trades"""
    for currency in CurrencyEnum.__members__:
        currency = CurrencyEnum(currency)
        fundamental_data = fundamental_data_repository.get_fundamental_data(
            currency=currency
        )
        if fundamental_data:
            if fundamental_data.aggregate_sentiment == SendimentEnum.BULLISH:
                open_trades()
            else:
                close_trades()
    pass


@inject
def close_trades():
    """Closes trades"""
    pass
