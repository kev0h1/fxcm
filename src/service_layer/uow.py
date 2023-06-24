import os
from mongoengine import connect, disconnect

from src.adapters.database.repositories.fundamental_repository import (
    FundamentalDataRepository,
)
from src.adapters.database.repositories.trade_repository import TradeRepository
from src.adapters.fxcm_connect.base_trade_connect import BaseTradeConnect
from src.service_layer.event_bus import TradingEventBus
from src.service_layer.handlers import handlers


class AbstractUnitOfWork:
    async def __aenter__(self):
        raise NotImplementedError

    async def __aexit__(self, *args):
        await self.rollback()

    async def publish(self):
        raise NotImplementedError


class MongoUnitOfWork(AbstractUnitOfWork):
    fundamental_data_repository: FundamentalDataRepository
    trade_repository = TradeRepository
    fxcm_connection = BaseTradeConnect

    def __init__(
        self, event_bus: TradingEventBus, fxcm_connection: BaseTradeConnect
    ):
        is_dev = os.environ.get("DOCKER", False)
        if is_dev:
            self.env = "mongo"
        else:
            self.env = "localhost"
        self.event_bus = event_bus
        self.fundamental_data_repository = FundamentalDataRepository()
        self.trade_repository = TradeRepository()
        self.fxcm_connection = fxcm_connection

        for event, handler in handlers.items():
            self.event_bus.subscribe(event, handler)

    async def __aenter__(self):
        _ = connect(host=f"mongodb://{self.env}/my_db")

    async def __aexit__(self, *args):
        disconnect()

    async def publish(self, event):
        self.event_bus.publish_events(event)
