from typing import List
from fastapi_restful import set_responses, Resource
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.models.db_connect import Database
from src.services.fundamental_service import FundamentalDataService
from src.container.container import Container
from src.api.routes.api_schema.schema import FundamentalSchema


class FundamentalResource(Resource):
    @inject
    def __init__(
        self,
        fundamental_data_service: FundamentalDataService = Depends(
            Provide[Container.fundamental_data_service],
        ),
        db: Database = Depends(Provide[Container.db]),
    ) -> None:
        super().__init__()
        self.service = fundamental_data_service
        self._db = db

    @set_responses(List[FundamentalSchema], 200)
    def get(
        self,
    ):
        """Deletes the database"""
        with self._db.get_session():
            return self.service.get_all_fundamental_data()
