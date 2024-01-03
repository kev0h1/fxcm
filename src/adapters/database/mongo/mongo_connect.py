from src.service_layer.uow import MongoUnitOfWork
from mongoengine import connection


class Database:
    def __init__(
        self,
        uow: MongoUnitOfWork,
    ) -> None:
        self.uow = uow

    async def reset_db(self, db_name="my_db") -> None:
        """Drop database"""
        async with self.uow:
            self.uow.client.drop_database(db_name)
