from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.entry_points.scheduler.get_fundamental_data import process_data


from src.adapters.scraper.forex_factory_scraper import (
    ForexFactoryScraper,
)
from src.logger import get_logger

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


@scheduler.scheduled_job("interval", seconds=300)
async def get_fundamental_trend_data():
    date_: datetime = datetime.today() - timedelta(days=3)
    # if date_.weekday
    if date_.weekday() < 5:
        logger.info(f"Getting fundamental data for {date_}")
        url = await ForexFactoryScraper.get_url_for_today(date_=date_)
        scraper = ForexFactoryScraper(url=url)
        objects = await scraper.get_fundamental_items()
        scraped_data = objects[-1]
        await process_data(scraper, objects, date_, scraped_data)
