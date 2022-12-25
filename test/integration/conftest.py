from src.models.db_connect import DbSession
from src.models.model import create_mappers, metadata_obj
import pytest


@pytest.fixture(autouse=True)
def reset_db():
    """Resets the database"""
    DbSession.init_engine()
    create_mappers()
    DbSession.reset_db(metadata=metadata_obj)
    yield
    DbSession.reset_db(metadata=metadata_obj)
