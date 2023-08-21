from datetime import datetime, timedelta, timezone
import os
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from tzlocal import get_localzone
from src.entry_points.scheduler.get_fundamental_data import process_data
from src.entry_points.scheduler.get_technical_signal import (
    get_technical_signal,
)

from src.entry_points.scheduler.manage_trades import manage_trades_handler
from src.entry_points.scheduler.manage_closed_trades import (
    manage_closed_trades,
)
import pytz
from src.logger import get_logger

logger = get_logger(__name__)

scheduler = AsyncIOScheduler()


@scheduler.scheduled_job("interval", seconds=115)
async def get_fundamental_trend_data():
    date_: datetime = (
        datetime.now(pytz.timezone("America/New_York"))
        if os.environ.get("DEPLOY_ENV", "local") == "aws"
        else datetime.now(get_localzone())
    )
    if date_.weekday() < 5:
        logger.info(f"Getting fundamental data for {date_}")
        await process_data(date_=date_)


@scheduler.scheduled_job("interval", seconds=300)
async def get_fundamental_technical_data():
    date_: datetime = datetime.now(timezone.utc)
    if date_.weekday() < 5:
        logger.info(f"Getting fundamental data for {date_}")
        await get_technical_signal()


@scheduler.scheduled_job("interval", seconds=75)
async def manage_trades():
    date_: datetime = datetime.now(timezone.utc)
    if date_.weekday() < 5:
        logger.info(f"Manage trades for date{date_}")
        await manage_trades_handler()


@scheduler.scheduled_job("interval", seconds=320)
async def manage_closed_trades_job():
    date_: datetime = datetime.now(timezone.utc)
    if date_.weekday() < 5:
        logger.info(f"Manage closed trades for date {date_}")
        await manage_closed_trades()
