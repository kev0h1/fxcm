import asyncio
from src.container.container import Container
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_restful import Api
from src.entry_points.routes.debug_routes import DebugResource, EventBusRoute
from src.entry_points.routes.fundamental_routes import FundamentalResource
from src.entry_points.routes.trade_routes import TradeResource, TradePl
from src.entry_points.scheduler.scheduler import scheduler
from src.logger import get_logger
from src.service_layer.uow import MongoUnitOfWork
import cProfile

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

    # do not push this
    profiler = cProfile.Profile()
    profiler.enable()

    api.add_resource(DebugResource(), "/debug", tags=["Debug"])
    api.add_resource(
        FundamentalResource(), "/fundamental-data", tags=["Fundamental Data"]
    )
    api.add_resource(TradeResource(), "/trades", tags=["Trade Data"])
    api.add_resource(TradePl(), "/trades-pl", tags=["Trade Profit and Loss"])

    api.add_resource(EventBusRoute(), "/event-bus", tags=["Event Bus"])

    @app.on_event("startup")
    async def start_up():
        scheduler.start()
        uow: MongoUnitOfWork = app.container.uow()
        # Access event_bus from the uow and start i
        asyncio.create_task(uow.event_bus.start())
        app.state.uow = uow
        app.state.event_bus = uow.event_bus

    @app.on_event("shutdown")
    async def shut_down():
        profiler.disable()  # Stop profiling
        profiler.dump_stats("profile_output.prof")

    return app
