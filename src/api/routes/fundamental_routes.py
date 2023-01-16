from typing import Any
from fastapi_restful import set_responses, Resource
from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.services.fundamental_service import FundamentalDataService
from src.container.container import Container


class FundamentalResource(Resource):
    @inject
    def __init__(
        self,
        fundamental_data_service: FundamentalDataService = Depends(
            Provide[Container.fundamental_data_service]
        ),
    ) -> None:
        super().__init__()
        self.service = fundamental_data_service

    @set_responses(Any, 200)
    def get(self):
        """Deletes the database"""
        return self.service.get_all_fundamental_data()
