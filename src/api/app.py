from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_restful import Api
from src.api.routes.debug_routes import DebugResource
from src.models.db_connect import DbSession
from src.models.model import create_mappers
from src.scheduler.scheduler import scheduler


def create_app():
    app = FastAPI()
    api = Api(app)
    origins = ["http://localhost:3000"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    DbSession.init_engine()
    create_mappers()
    api.add_resource(DebugResource(), "/delete", tags=["Debug"])

    @app.on_event("startup")
    async def start_up():
        scheduler.start()

    return app
