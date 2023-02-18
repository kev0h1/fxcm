from src.models.mongo_connect import Database
import pytest


@pytest.fixture(autouse=True)
def get_db():
    """Resets the database"""
    db = Database()
    db.reset_db()
    yield db
    db.reset_db()
