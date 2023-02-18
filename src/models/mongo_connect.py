from contextlib import contextmanager

from mongoengine import connect, disconnect
import pymongo


class Database:
    def reset_db(self):
        """Drop database"""
        client = pymongo.MongoClient("localhost", 27017)
        client.drop_database("my_db")

    @contextmanager
    def get_session(self):
        session = connect(host="mongodb://127.0.0.1:27017/my_db")
        try:
            print("opening")
            yield session
        except Exception:
            # logger.exception("Session rollback because of exception")
            raise
        finally:
            disconnect()
