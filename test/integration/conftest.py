from src.models.db_connect import Database
from src.models.model import create_mappers, metadata_obj
import pytest

create_mappers()


@pytest.fixture(autouse=True)
def reset_db():
    """Resets the database"""
    Database.init_engine()
    Database.reset_db(metadata=metadata_obj)
    yield
    Database.reset_db(metadata=metadata_obj)
