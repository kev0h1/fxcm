from src.models.db_connect import DbSession
from src.models.model import create_mappers, metadata_obj
import pytest

create_mappers()


@pytest.fixture(autouse=True)
def reset_db():
    """Resets the database"""
    DbSession.init_engine()
    DbSession.reset_db(metadata=metadata_obj)
    yield
    DbSession.reset_db(metadata=metadata_obj)
