from dependency_injector import containers, providers
from src.adapters.database.mongo.mongo_connect import Database
from src.service_layer.fundamental_service import FundamentalDataService
from src.service_layer.uow import MongoUnitOfWork


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
    uow = providers.Singleton(MongoUnitOfWork)

    fundamental_data_service = providers.Factory(
        FundamentalDataService,
        uow=uow,
    )
