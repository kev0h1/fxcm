from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.entry_points.scheduler.get_fundamental_data import process_data
from src.entry_points.scheduler.get_technical_signal import (
    get_technical_signal,
)

from src.entry_points.scheduler.manage_trades import manage_trades
from src.entry_points.scheduler.manage_closed_trades import (
    manage_closed_trades,
)

from src.logger import get_logger

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


@scheduler.scheduled_job("interval", seconds=300)
async def get_fundamental_trend_data():
    date_: datetime = datetime.today()
    if date_.weekday() < 5:
        logger.info(f"Getting fundamental data for {date_}")
        await process_data(date_=date_)


@scheduler.scheduled_job("interval", seconds=300)
async def get_fundamental_technical_data():
    date_: datetime = datetime.today()
    if date_.weekday() < 5:
        logger.info(f"Getting fundamental data for {date_}")
        await get_technical_signal()


@scheduler.scheduled_job("interval", seconds=60)
async def manage_trades():
    date_: datetime = datetime.today()
    if date_.weekday() < 5:
        logger.info(f"Manage trades for date{date_}")
        await manage_trades()


@scheduler.scheduled_job("interval", seconds=300)
async def manage_closed_trades():
    date_: datetime = datetime.today()
    if date_.weekday() < 5:
        logger.info(f"Manage closed trades for date {date_}")
        await manage_closed_trades()
