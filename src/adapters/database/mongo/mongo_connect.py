import pymongo
import os


class Database:
    def __init__(self):
        is_dev = os.environ.get("DOCKER", False)
        if is_dev:
            self.env = "mongo"
        else:
            self.env = "localhost"

        self.client = pymongo.MongoClient(self.env, 27017)

    async def reset_db(self):
        """Drop database"""
        self.client.drop_database("my_db")
