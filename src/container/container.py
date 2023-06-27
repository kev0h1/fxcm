from dependency_injector import containers, providers
from src.adapters.database.mongo.mongo_connect import Database
from src.service_layer.fundamental_service import FundamentalDataService
from src.service_layer.trade_service import TradeService
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
    event_bus = providers.Singleton(TradingEventBus)
    fxcm_connection = providers.Singleton(MockTradeConnect, {})

    uow = providers.Singleton(MongoUnitOfWork, event_bus, fxcm_connection)

    fundamental_data_service = providers.Factory(
        FundamentalDataService,
        uow=uow,
    )

    trade_service = providers.Factory(TradeService, uow=uow)

    indicator_service = providers.Factory(Indicators)
