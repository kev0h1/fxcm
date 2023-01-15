from datetime import datetime
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
from src.classes.fundamental import FundamentalData, FundamentalTrend

from src.indicators.forex_factory_scraper import ForexFactoryScraper
from sqlalchemy.orm import Session
from src.models.db_connect import DbSession

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
    with DbSession.session.begin() as session:
        process_fundamental_data_items(session, fundamental_data_items)


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


def process_fundamental_data_items(
    session: Session,
    items: List[FundamentalData],
):
    for data in reversed(items):
        fundamental_data: FundamentalData = (
            FundamentalData.get_fundamental_data(
                session=session,
                currency=data.currency,
                last_updated=data.last_updated,
            )
        )

        if not fundamental_data:
            session.add(data)
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
