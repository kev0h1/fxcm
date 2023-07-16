import uuid
from src.adapters.database.mongo.mongo_connect import Database
import pytest


@pytest.fixture()
def get_db() -> None:
    # Generate a unique database name for each test
    db = Database()
    db_name = "mydb_test_" + str(uuid.uuid4())
    # Connect to the test database
    yield db_name
    db.client.drop_database(db_name)
