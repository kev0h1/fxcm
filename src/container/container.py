from dependency_injector import containers, providers
from src.adapters.database.mongo.mongo_connect import Database
from src.service_layer.fundamental_service import FundamentalDataService
from src.service_layer.uow import MongoUnitOfWork
from src.service_layer.event_bus import TradingEventBus


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.entry_points.routes.fundamental_routes",
            "src.entry_points.routes.debug_routes",
            "src.entry_points.scheduler.scheduler",
            "src.adapters.fxcm_connect.fxcm_connect",
        ]
    )
    db = providers.Singleton(Database)
    event_bus = providers.Singleton(TradingEventBus)

    uow = providers.Singleton(MongoUnitOfWork, event_bus)

    fundamental_data_service = providers.Factory(
        FundamentalDataService,
        uow=uow,
    )
