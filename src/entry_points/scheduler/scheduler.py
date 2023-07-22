from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.entry_points.scheduler.get_fundamental_data import process_data
from src.entry_points.scheduler.get_technical_signal import (
    get_technical_signal,
)

from src.logger import get_logger

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


@scheduler.scheduled_job("interval", seconds=300)
async def get_fundamental_trend_data():
    date_: datetime = datetime.today() - timedelta(days=3)
    if date_.weekday() < 5:
        logger.info(f"Getting fundamental data for {date_}")
        await process_data(date_=date_)


@scheduler.scheduled_job("interval", seconds=300)
async def get_fundamental_trend_data():
    date_: datetime = datetime.today() - timedelta(days=3)
    if date_.weekday() < 5:
        logger.info(f"Getting fundamental data for {date_}")
        await get_technical_signal()
