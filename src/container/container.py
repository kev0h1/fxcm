from dependency_injector import containers, providers
from src.adapters.database.mongo.mongo_connect import Database
from src.adapters.fxcm_connect.oanda_connect import OandaConnect
from src.adapters.scraper.forex_factory_scraper import ForexFactoryScraper
from src.service_layer.fundamental_service import FundamentalDataService
from src.service_layer.trade_service import TradeService
from src.service_layer.uow import MongoUnitOfWork
from src.service_layer.indicators import Indicators


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.entry_points.routes.fundamental_routes",
            "src.entry_points.routes.trade_routes",
            "src.entry_points.routes.debug_routes",
            "src.entry_points.scheduler.scheduler",
        ]
    )

    fxcm_connection = providers.Singleton(OandaConnect)
    scraper = providers.Singleton(ForexFactoryScraper)

    uow = providers.Singleton(MongoUnitOfWork, fxcm_connection, scraper)

    db = providers.Singleton(Database, uow)

    fundamental_data_service = providers.Factory(
        FundamentalDataService,
        uow=uow,
    )

    trade_service = providers.Factory(TradeService, uow=uow)

    indicator_service = providers.Factory(Indicators)
