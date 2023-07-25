from dependency_injector import containers, providers
from src.adapters.database.mongo.mongo_connect import Database
from src.adapters.fxcm_connect.oanda_connect import OandaConnect
from src.adapters.scraper.forex_factory_scraper import ForexFactoryScraper
from src.service_layer.fundamental_service import FundamentalDataService
from src.service_layer.uow import MongoUnitOfWork
from src.service_layer.event_bus import TradingEventBus
from src.adapters.fxcm_connect.mock_trade_connect import MockTradeConnect
from src.service_layer.indicators import Indicators


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.entry_points.routes.fundamental_routes",
            "src.entry_points.routes.debug_routes",
            "src.entry_points.scheduler.scheduler",
        ]
    )
    db = providers.Singleton(Database)
    fxcm_connection = providers.Singleton(OandaConnect)
    scraper = providers.Singleton(ForexFactoryScraper)

    uow = providers.Singleton(MongoUnitOfWork, fxcm_connection, scraper)

    fundamental_data_service = providers.Factory(
        FundamentalDataService,
        uow=uow,
    )

    indicator_service = providers.Factory(Indicators)
