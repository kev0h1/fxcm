from contextlib import contextmanager

from mongoengine import connect, disconnect
import pymongo
import os


class Database:
    def __init__(self) -> None:
        is_dev = os.environ.get("DOCKER", False)
        if is_dev:
            self.env = "mongo"
        else:
            self.env = "localhost"

    async def reset_db(self):
        """Drop database"""

        client = pymongo.MongoClient(self.env, 27017)
        client.drop_database("my_db")

    @contextmanager
    def get_session(self):
        session = connect(host=f"mongodb://{self.env}/my_db")
        try:
            print("opening")
            yield session
        except Exception:
            # logger.exception("Session rollback because of exception")
            raise
        finally:
            disconnect()
