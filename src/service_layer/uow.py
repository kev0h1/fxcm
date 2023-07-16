import os
from mongoengine import connect, disconnect

from src.adapters.database.repositories.fundamental_repository import (
    FundamentalDataRepository,
)
from src.adapters.database.repositories.trade_repository import TradeRepository
from src.adapters.fxcm_connect.base_trade_connect import BaseTradeConnect

from src.service_layer.event_bus import TradingEventBus
from src.service_layer.handlers import handlers
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.adapters.scraper.base_scraper import BaseScraper


class AbstractUnitOfWork:
    async def __aenter__(self):
        raise NotImplementedError

    async def __aexit__(self, *args):
        await self.rollback()

    async def publish(self):
        raise NotImplementedError


class MongoUnitOfWork(AbstractUnitOfWork):
    def __init__(
        self,
        fxcm_connection: BaseTradeConnect,
        scraper: "BaseScraper",
        db_name: str = "my_db",
    ):
        is_dev = os.environ.get("DOCKER", False)
        if is_dev:
            self.env = "mongo"
        else:
            self.env = "localhost"
        self.db_name = db_name
        self.event_bus = TradingEventBus(uow=self)
        self.fundamental_data_repository: FundamentalDataRepository = (
            FundamentalDataRepository()
        )
        self.trade_repository: TradeRepository = TradeRepository()
        self.fxcm_connection: BaseTradeConnect = fxcm_connection
        self.scraper: "BaseScraper" = scraper

        for event, handler in handlers.items():
            self.event_bus.subscribe(event, handler)

    async def __aenter__(self):
        _ = connect(host=f"mongodb://{self.env}/{self.db_name}")

    async def __aexit__(self, *args):
        disconnect()

    async def publish(self, event):
        await self.event_bus.publish(event)
