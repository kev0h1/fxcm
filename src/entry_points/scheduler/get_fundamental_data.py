from datetime import datetime
from typing import List, Tuple, Union
from xml.dom import NotFoundErr
from src.container.container import Container
from src.domain.errors.errors import NotFound

from src.service_layer.fundamental_service import FundamentalDataService
from src.service_layer.uow import MongoUnitOfWork

from src.domain.fundamental import CalendarEvent, FundamentalData
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.config import CurrencyEnum

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
) -> List[FundamentalData]:
    """Converts the fundamental data into objects we can manipulate"""
    async with uow:
        await uow.scraper.set_scraper_params(date_=date_)
        await uow.scraper.make_request()
        scraped_items: list[
            Tuple[CalendarEvent, CurrencyEnum, datetime]
        ] = await uow.scraper.get_scraped_calendar_items(uow=uow)
        for scraped_calendar_event, currency, date_time in scraped_items:
            if scraped_calendar_event:
                intiate_close_trade_event = False
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
                elif (
                    not calender_event.actual
                    or not calender_event.forecast
                    or not calender_event.previous
                ):
                    logger.info(
                        "Updating calendar event for event %s and currency %s"
                        % (scraped_calendar_event.calendar_event, currency)
                    )
                    calender_event.actual = scraped_calendar_event.actual
                    calender_event.previous = scraped_calendar_event.previous
                    calender_event.forecast = scraped_calendar_event.forecast

                    calender_event.sentiment = scraped_calendar_event.sentiment
                    logger.info(
                        "Sentiment updated for currency: {currency} to {sentiment}"
                    )
                    intiate_close_trade_event = True

                logger.info("Calculating aggregate score")
                await fundamental_data_service.calculate_aggregate_score(
                    fundamental_data=fundamental_data
                )
                await uow.fundamental_data_repository.save(fundamental_data)
                if intiate_close_trade_event:
                    logger.info(
                        "Initiating close trade event for currency %s and sentiments that are not %s"
                        % (currency, scraped_calendar_event.sentiment)
                    )
                    await uow.event_bus.publish(
                        CloseTradeEvent(
                            currency=currency,
                            sentiment=calender_event.sentiment,
                        )
                    )


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
            lambda x: x.calendar_event == calendar_event,
            fundamental_data.calendar_events,
        ),
        None,
    )
