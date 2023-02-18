from dependency_injector import containers, providers
from src.models.mongo_connect import Database
from src.repositories.fundamental_repository import FundamentalDataRepository
from src.services.fundamental_service import FundamentalDataService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.api.routes.fundamental_routes",
            "src.api.routes.debug_routes",
            "src.scheduler.scheduler",
            "src.fxcm_connect.fxcm_connect",
        ]
    )
    db = providers.Singleton(Database)

    fundamental_data_repository = providers.Factory(FundamentalDataRepository)

    fundamental_data_service = providers.Factory(
        FundamentalDataService,
        fundamental_data_repository=fundamental_data_repository,
    )
