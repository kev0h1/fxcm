from dependency_injector import containers, providers
from src.adapters.database.mongo.mongo_connect import Database
from src.adapters.database.repositories.fundamental_repository import FundamentalDataRepository
from src.service_layer.fundamental_service import FundamentalDataService


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

    fundamental_data_repository = providers.Factory(FundamentalDataRepository)

    fundamental_data_service = providers.Factory(
        FundamentalDataService,
        fundamental_data_repository=fundamental_data_repository,
    )
