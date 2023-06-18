from src.domain import events


async def close_trade_handler(event: events.Event):
    """Handles a close trade event"""
    print(f"Close trade event: {event.currency}")


handlers = {events.CloseTradeEvent: close_trade_handler}
