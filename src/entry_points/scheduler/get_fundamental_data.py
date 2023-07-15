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

                logger.info("Calculating aggregate score")
                await fundamental_data_service.calculate_aggregate_score(
                    fundamental_data=fundamental_data
                )
                await uow.fundamental_data_repository.save(fundamental_data)
                fundamental_data_list.append(fundamental_data)
        await generate_event(uow, fundamental_data_list, currency)


async def generate_event(
    uow: MongoUnitOfWork,
    fundamental_data_list: list[FundamentalData],
    currency: CurrencyEnum,
) -> None:
    for data in fundamental_data_list:
        can_process_close_event = await has_pending_calendar_updates(data)
        if (
            data.processed is False
            and data.aggregate_sentiment != SentimentEnum.FLAT
            and can_process_close_event
        ):
            logger.info(
                "Initiating close trade event for currency %s and sentiments that are not %s"
                % (data.currency, data.aggregate_sentiment)
            )
            await uow.publish(
                CloseTradeEvent(
                    currency=currency,
                    sentiment=data.aggregate_sentiment,
                )
            )
            data.processed = True
            uow.fundamental_data_repository.save(data)


async def has_pending_calendar_updates(data: FundamentalData) -> bool:
    can_process_close_event = True
    for calendar_event in data.calendar_events:
        if any(
            value is None
            for value in [
                calendar_event.actual,
                calendar_event.previous,
                calendar_event.forecast,
            ]
        ) and not all(
            value is None
            for value in [
                calendar_event.actual,
                calendar_event.previous,
                calendar_event.forecast,
            ]
        ):
            logger.info(
                "There are pending calendar updates for calendar event %s"
                % calendar_event.calendar_event
            )
            can_process_close_event = False
        else:
            logger.info(
                "There are no pending calendar updates for calendar event %s"
                % calendar_event.calendar_event
            )
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
