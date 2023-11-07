from datetime import datetime
from typing import List, Tuple, Union
from src.container.container import Container
from src.domain.errors.errors import NotFound
from src.service_layer.fundamental_service import FundamentalDataService  # type: ignore
from src.service_layer.uow import MongoUnitOfWork
from src.domain.fundamental import CalendarEvent, FundamentalData  # type: ignore
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.config import CurrencyEnum, SentimentEnum
from src.domain.events import CloseTradeEvent
from src.logger import get_logger


logger = get_logger(__name__)


@inject
async def process_data(
    date_: datetime,
    load_data=False,
    uow: MongoUnitOfWork = Depends(Provide[Container.uow]),
    fundamental_data_service: FundamentalDataService = Depends(
        Provide[Container.fundamental_data_service]
    ),
) -> None:
    """Converts the fundamental data into objects we can manipulate"""
    async with uow:
        await uow.scraper.set_scraper_params(date_=date_)
        await uow.scraper.make_request()
        scraped_items: list[
            Tuple[CalendarEvent, CurrencyEnum, datetime]
        ] = await uow.scraper.get_scraped_calendar_items(uow=uow)
        fundamental_data_list: List[FundamentalData] = []
        for scraped_calendar_event, currency, date_time in scraped_items:
            if scraped_calendar_event:
                fundamental_data: FundamentalData = (
                    await uow.fundamental_data_repository.get_fundamental_data(
                        currency=currency, last_updated=date_time
                    )
                )
                if not fundamental_data:
                    logger.error(
                        "expected fundamental data for currency %s and last_updated %s"
                        % (currency, date_time)
                    )
                    raise NotFound(
                        "expected fundamental data for currency %s and last_updated %s"
                        % (currency, date_time)
                    )
                calender_event = await get_calendar_event(
                    fundamental_data, scraped_calendar_event
                )
                if not calender_event:
                    fundamental_data.calendar_events.append(
                        scraped_calendar_event
                    )
                elif fundamental_data.processed is False or load_data:
                    calender_event.actual = scraped_calendar_event.actual
                    calender_event.previous = scraped_calendar_event.previous
                    calender_event.forecast = scraped_calendar_event.forecast
                    calender_event.sentiment = scraped_calendar_event.sentiment

                await fundamental_data_service.calculate_aggregate_score(
                    fundamental_data=fundamental_data
                )
                await uow.fundamental_data_repository.save(fundamental_data)
                fundamental_data_list.append(fundamental_data)
            if not load_data:
                await generate_event(uow, fundamental_data_list, currency)
            else:
                fundamental_data.processed = True
                await uow.fundamental_data_repository.save(fundamental_data)


async def generate_event(
    uow: MongoUnitOfWork,
    fundamental_data_list: list[FundamentalData],
    currency: CurrencyEnum,
) -> None:
    for data in fundamental_data_list:
        can_process_close_event = await calendar_updates_complete(data)
        if data.processed is False and can_process_close_event:
            logger.info(
                "Initiating close trade event for currency %s and sentiments that are not %s"
                % (data.currency, data.aggregate_sentiment)
            )
            if data.aggregate_sentiment != SentimentEnum.FLAT:
                await uow.publish(
                    CloseTradeEvent(
                        currency=currency,
                        sentiment=data.aggregate_sentiment,
                    )
                )
            data.processed = True
            await uow.fundamental_data_repository.save(data)


async def calendar_updates_complete(data: FundamentalData) -> bool:
    can_process_close_event = True
    for calendar_event in data.calendar_events:
        if any(
            value is None
            for value in [
                calendar_event.actual,
                calendar_event.previous,
                calendar_event.forecast,
            ]
        ):
            can_process_close_event = False
    return can_process_close_event


async def get_calendar_event(
    fundamental_data: FundamentalData,
    calendar_event: CalendarEvent,
) -> Union[CalendarEvent, None]:
    """Retrieves a calendar event from a fundamental data object

    Returns:
        Union[CalendarEvent, None]: _description_
    """
    return next(
        filter(
            lambda x: x.calendar_event == calendar_event.calendar_event,
            fundamental_data.calendar_events,
        ),
        None,
    )


async def process_fundamental_data(
    date_: datetime,
    uow: MongoUnitOfWork = Depends(Provide[Container.uow]),
    fundamental_data_service: FundamentalDataService = Depends(
        Provide[Container.fundamental_data_service]
    ),
) -> None:
    """Processes the fundamental data for a given date"""
    async with uow:
        fundamental_data = (
            await fundamental_data_service.get_fundamental_data_for_unprocessed_events()
        )
        for data in fundamental_data:
            timedelta = date_ - data.last_updated
            if timedelta.total_seconds() > (60 * 10):
                data.processed = True
                await uow.fundamental_data_repository.save(data)
