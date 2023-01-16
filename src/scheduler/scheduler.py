from datetime import datetime
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.container.container import Container

from src.services.fundamental_service import FundamentalDataService

scheduler = AsyncIOScheduler()
from src.classes.fundamental import FundamentalData
from dependency_injector.wiring import inject, Provide
from fastapi import Depends


from src.indicators.forex_factory_scraper import ForexFactoryScraper

# @scheduler.scheduled_job("interval")
def get_fundamental_trend_data():
    date_: datetime = datetime(2022, 12, 2)
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
    fundamental_data_service: FundamentalDataService = Depends(
        Provide[Container.fundamental_data_service]
    ),
):
    for data in reversed(items):
        fundamental_data = (
            fundamental_data_service.get_fundamental_data_by_currency_datetime(
                data.currency, data.last_updated
            )
        )
        if not fundamental_data:
            fundamental_data_service.create_fundamental_data(data)
        elif not data.actual or not data.forecast or not data.previous:
            fundamental_data.actual = data.actual
            fundamental_data.previous = data.previous
            fundamental_data.forecast = data.forecast
            fundamental_data.sentiment = data.sentiment

        # if data.actual:
        #     trend: FundamentalTrend = (
        #         FundamentalTrend.get_trend_data_for_currency(
        #             session=session, currency=data.currency
        #         )
        #     )

        #     if not trend:
        #         trend = FundamentalTrend(
        #             last_updated=data.last_updated, currency=data.currency
        #         )
        #         session.add(trend)
