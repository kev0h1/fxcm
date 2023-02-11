from src.models.db_connect import Database
from src.models.model import create_mappers, metadata_obj
import pytest

create_mappers()


@pytest.fixture(autouse=True)
def get_db():
    """Resets the database"""
    db = Database()
    db.reset_db(metadata=metadata_obj)
    yield db
    db.reset_db(metadata=metadata_obj)
