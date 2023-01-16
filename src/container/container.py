from dependency_injector import containers, providers
from src.models.db_connect import Database
from src.repositories.fundamental_repository import FundamentalDataRepository
from src.services.fundamental_service import FundamentalDataService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "src.api.routes.fundamental_routes",
            "src.api.routes.debug_routes",
            "src.scheduler.scheduler",
        ]
    )
    db = providers.Singleton(Database)

    fundamnetal_data_repository = providers.Factory(
        FundamentalDataRepository,
        session_factory=db.provided.session,
    )

    fundamental_data_service = providers.Factory(
        FundamentalDataService,
        fundamental_data_repository=fundamnetal_data_repository,
    )
