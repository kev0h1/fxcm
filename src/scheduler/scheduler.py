from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# @scheduler.scheduled_job("interval", min=5)
# def get_trend_data():
#     pass
