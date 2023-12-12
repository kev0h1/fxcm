import uuid

from mock import MagicMock
from src.adapters.database.mongo.mongo_connect import Database
import pytest
from contextlib import asynccontextmanager
from src.service_layer.uow import MongoUnitOfWork


# fix me how can a yield an async generator
@pytest.fixture()
def get_db() -> None:
    # Generate a unique database name for each test

    db_name = "mydb_test_" + str(uuid.uuid4())
    uow = MongoUnitOfWork(
        fxcm_connection=MagicMock(),
        db_name=db_name,
        scraper=MagicMock(),
        sentiment_scraper=MagicMock(),
    )
    db = Database(uow=uow)
    # Connect to the test database
    yield db_name
    db.reset_db(db_name)
