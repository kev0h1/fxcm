from datetime import datetime
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.container.container import Container
from src.models.mongo_connect import Database

from src.repositories.fundamental_repository import FundamentalDataRepository

scheduler = AsyncIOScheduler()
from src.classes.fundamental import FundamentalData
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.config import CurrencyEnum

from src.indicators.forex_factory_scraper import (
    CALENDAR_CURRENCY,
    ForexFactoryScraper,
)

# @scheduler.scheduled_job("interval")
def get_fundamental_trend_data():
    date_: datetime = datetime(2023, 2, 1)
    url = ForexFactoryScraper.get_url_for_today(date_=date_)
    scraper = ForexFactoryScraper(url=url)
    objects = scraper.get_fundamental_items()
    scraped_data = objects[-1]
    process_data(scraper, objects, date_, scraped_data)


@inject
def process_data(
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
) -> List[FundamentalData]:
    """Converts the fundamental data into objects we can manipulate"""
    with db.get_session():
        for index, data in enumerate(scraped_data):
            time = scraper.get_time_value(objects, -1, index)
            if time is None:
                continue
            date_time = datetime.combine(date_, time)
            currency = scraper.get_event_values(
                element=data, class_name=CALENDAR_CURRENCY
            )
            if currency not in CurrencyEnum.__members__:
                continue
            currency = CurrencyEnum(currency)
            scraped_calendar_event = scraper.create_calendar_event(tag=data)

            if scraped_calendar_event:
                fundamental_data = (
                    fundamental_data_repository.get_fundamental_data(
                        currency=currency, last_updated=date_time
                    )
                )
                if not fundamental_data:
                    fundamental_data = scraper.create_fundamental_object(
                        date_, data, time
                    )
                    fundamental_data = fundamental_data_repository.save(
                        fundamental_data
                    )
                calender_event = (
                    fundamental_data_repository.get_calendar_event(
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
                fundamental_data_repository.save(fundamental_data)
