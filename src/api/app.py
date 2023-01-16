from src.container.container import Container
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_restful import Api
from src.api.routes.debug_routes import DebugResource
from src.api.routes.fundamental_routes import FundamentalResource
from src.models.model import create_mappers
from src.scheduler.scheduler import scheduler


def create_app():
    container = Container()
    create_mappers()
    app = FastAPI()
    app.container = container
    api = Api(app)
    origins = ["http://localhost:3000"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    api.add_resource(DebugResource(), "/debug", tags=["Debug"])
    api.add_resource(
        FundamentalResource(), "/fundamental-data", tags=["Fundamental Data"]
    )

    @app.on_event("startup")
    async def start_up():
        scheduler.start()

    return app
