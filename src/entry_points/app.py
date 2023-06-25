from src.container.container import Container
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_restful import Api
from src.entry_points.routes.debug_routes import DebugResource
from src.entry_points.routes.fundamental_routes import FundamentalResource
from src.entry_points.scheduler.scheduler import scheduler
from src.logger import get_logger

logger = get_logger(__name__)


def create_app():
    logger.info("Creating app")
    container = Container()
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
