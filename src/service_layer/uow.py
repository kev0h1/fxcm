import json
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

from src.logger import get_logger

logger = get_logger(__name__)


from src.utils import get_secret

if TYPE_CHECKING:
    from src.adapters.scraper.base_scraper import BaseScraper

# Use this code snippet in your app.
# If you need more information about configurations
# or implementing the sample code, visit the AWS docs:
# https://aws.amazon.com/developer/language/python/


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
        self.db_name = db_name
        if os.environ.get("DEPLOY_ENV", "local") == "aws":
            logger.info("Using AWS DocDB")
            secret = get_secret("DocumentDBSecret")
            username, password = secret["username"], secret["pass"]
            docdb_cluster_endpoint = "mydbcluster.cluster-cj2g1svpqisv.us-east-1.docdb.amazonaws.com"
            self.pem_path = "./global-bundle.pem"
            self.host = f"mongodb://{username}:{password}@{docdb_cluster_endpoint}:27017/?tls=true&tlsCAFile={self.pem_path}&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false"

        else:
            logger.info("Using local MongoDB")
            self.host = f"mongodb://localhost"
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
        self.client = connect(self.db_name, host=self.host)

    async def __aexit__(self, *args):
        disconnect()

    async def publish(self, event):
        await self.event_bus.publish(event)
