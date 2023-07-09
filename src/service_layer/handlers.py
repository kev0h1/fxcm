from __future__ import annotations
from src.config import CurrencyEnum, PositionEnum, SentimentEnum
from src.domain import events
from typing import TYPE_CHECKING

from src.domain.trade import Trade

if TYPE_CHECKING:
    from src.service_layer.uow import MongoUnitOfWork

from src.logger import get_logger


logger = get_logger(__name__)


async def close_trade_handler(
    event: events.CloseTradeEvent, uow: MongoUnitOfWork
):
    """Handles a close trade event"""
    logger.info(
        "Handling close trade event for currency %s with sentiment %s"
        % (event.currency, event.sentiment)
    )
    trades: list[Trade] = []
    if event.sentiment == SentimentEnum.BULLISH:
        trades = await uow.trade_repository.get_bearish_trades(event.currency)
    elif event.sentiment == SentimentEnum.BEARISH:
        trades = await uow.trade_repository.get_bullish_trades(event.currency)

    for trade in trades:
        await uow.fxcm_connection.close_trade(
            trade_id=trade.trade_id, amount=trade.position_size
        )
        trade.position = PositionEnum.CLOSED
        await uow.trade_repository.save(trade)


async def open_trade_handler(
    event: events.OpenTradeEvent, uow: MongoUnitOfWork
):
    ...


async def create_trade_handler(
    event: events.CreateTradeEvent, uow: MongoUnitOfWork
):
    """Create a trade after initiated by forex partner"""
    forex_pair = event.forex_pair.value.split("/")
    trade = Trade(
        trade_id=event.trade_id,
        position_size=event.position_size,
        stop=event.stop,
        limit=event.limit,
        is_buy=event.is_buy,
        forex_currency_pair=event.forex_pair,
        base_currency=CurrencyEnum(forex_pair[0]),
        quote_currency=CurrencyEnum(forex_pair[1]),
    )
    uow.trade_repository.save(trade)


handlers = {
    events.CloseTradeEvent: close_trade_handler,
    events.OpenTradeEvent: open_trade_handler,
    events.CreateTradeEvent: create_trade_handler,
}
