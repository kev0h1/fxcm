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


from src.indicators.forex_factory_scraper import ForexFactoryScraper

# @scheduler.scheduled_job("interval")
def get_fundamental_trend_data():
    date_: datetime = datetime(2023, 1, 31)
    url = ForexFactoryScraper.get_url_for_today(date_=date_)
    scraper = ForexFactoryScraper(url=url)
    objects = scraper.get_fundamental_items()
    scraped_data = objects[-1]
    fundamental_data_items: List[FundamentalData] = get_fundamental_data_items(
        scraper, objects, date_, scraped_data
    )
    process_fundamental_data_items(fundamental_data_items)


def get_fundamental_data_items(
    scraper: ForexFactoryScraper, objects, date_, scraped_data
) -> List[FundamentalData]:
    """Converts the fundamental data into objects we can manipulate"""
    fundamental_data_items = []
    for index, data in enumerate(scraped_data):
        time = scraper.get_time_value(objects, -1, index)
        fundamental_data = scraper.create_fundamental_data_object(
            date_=date_, tag=data, time=time
        )
        if fundamental_data:
            fundamental_data_items.append(fundamental_data)

    return fundamental_data_items


@inject
def process_fundamental_data_items(
    items: List[FundamentalData],
    fundamental_data_repository: FundamentalDataRepository = Depends(
        Provide[Container.fundamental_data_repository]
    ),
    db: Database = Depends(
        Provide[Container.db],
    ),
):
    with db.get_session():
        for data in reversed(items):
            fundamental_data = (
                fundamental_data_repository.get_fundamental_data(
                    data.currency, data.last_updated
                )
            )
            if not fundamental_data:
                fundamental_data_repository.add(data)
            elif not data.actual or not data.forecast or not data.previous:
                fundamental_data.actual = data.actual
                fundamental_data.previous = data.previous
                fundamental_data.forecast = data.forecast
                fundamental_data.sentiment = data.sentiment
