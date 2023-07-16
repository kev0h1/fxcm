import pymongo
import os


class Database:
    def __init__(self) -> None:
        is_dev = os.environ.get("DOCKER", False)
        if is_dev:
            self.env = "mongo"
        else:
            self.env = "localhost"

        self.client = pymongo.MongoClient(self.env, 27017)

    async def reset_db(self, db_name="my_db") -> None:
        """Drop database"""
        self.client.drop_database(db_name)
