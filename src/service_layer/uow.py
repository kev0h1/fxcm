import os
from mongoengine import connect, disconnect

from src.adapters.database.repositories.fundamental_repository import (
    FundamentalDataRepository,
)
from src.adapters.database.repositories.trade_repository import TradeRepository
from src.service_layer.event_bus import TradingEventBus
from src.service_layer.handlers import handlers


class AbstractUnitOfWork:
    async def __aenter__(self):
        raise NotImplementedError

    async def __aexit__(self, *args):
        await self.rollback()

    async def commit(self):
        raise NotImplementedError

    async def rollback(self):
        raise NotImplementedError


class MongoUnitOfWork(AbstractUnitOfWork):
    fundamental_data_repository: FundamentalDataRepository
    trade_repository = TradeRepository

    def __init__(self, event_bus: TradingEventBus):
        is_dev = os.environ.get("DOCKER", False)
        if is_dev:
            self.env = "mongo"
        else:
            self.env = "localhost"
        self.event_bus = event_bus
        self.fundamental_data_repository = FundamentalDataRepository()
        self.trade_repository = TradeRepository()
        for event, handler in handlers.items():
            self.event_bus.subscribe(event, handler)

    async def __aenter__(self):
        _ = connect(host=f"mongodb://{self.env}/my_db")

    async def __aexit__(self, *args):
        disconnect()

    async def commit(self, event):
        self.event_bus.publish_events()

    async def rollback(self):
        self.session.rollback()
