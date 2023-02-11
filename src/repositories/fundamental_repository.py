import datetime
from typing import Iterator
from src.classes.fundamental import FundamentalData

from sqlalchemy.orm import Session

from src.config import CurrencyEnum
from src.models.db_connect import context
from src.repositories.base_repository import BaseRepository


class FundamentalDataRepository(BaseRepository):
    def get_all(self) -> Iterator[FundamentalData]:
        session: Session = context.get("session")
        print(session)
        return session.query(FundamentalData).all()

    def get_fundamental_data(
        self, currency: CurrencyEnum, last_updated: datetime
    ) -> FundamentalData:
        session: Session = context.get("session")
        return (
            session.query(FundamentalData)
            .filter_by(currency=currency, last_updated=last_updated)
            .one_or_none()
        )


# class NotFoundError(Exception):

#     entity_name: str

#     def __init__(self, entity_id):
#         super().__init__(f"{self.entity_name} not found, id: {entity_id}")


# class UserNotFoundError(NotFoundError):

#     entity_name: str = "User"
