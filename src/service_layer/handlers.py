from __future__ import annotations
from src.config import PositionEnum, SentimentEnum
from src.domain import events
from typing import TYPE_CHECKING

from src.domain.trade import Trade

if TYPE_CHECKING:
    from src.service_layer.uow import MongoUnitOfWork


async def close_trade_handler(
    event: events.CloseTradeEvent, uow: MongoUnitOfWork
):
    """Handles a close trade event"""
    print(f"Close trade event: {event.currency}")
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


handlers = {
    events.CloseTradeEvent: close_trade_handler,
    events.OpenTradeEvent: open_trade_handler,
}
