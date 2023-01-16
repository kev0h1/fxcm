from contextlib import AbstractContextManager
import datetime
from typing import Callable, Iterator
from src.classes.fundamental import FundamentalData

from sqlalchemy.orm import Session

from src.config import CurrencyEnum


class FundamentalDataRepository:
    def __init__(
        self, session_factory: Callable[..., AbstractContextManager[Session]]
    ) -> None:
        self.session_factory = session_factory

    def get_all(self) -> Iterator[FundamentalData]:
        with self.session_factory() as session:
            return session.query(FundamentalData).all()

    def get_fundamental_data(
        self, currency: CurrencyEnum, last_updated: datetime
    ) -> FundamentalData:
        with self.session_factory() as session:
            return (
                session.query(FundamentalData)
                .filter_by(currency=currency, last_updated=last_updated)
                .one_or_none()
            )

    def add(self, fundamental_data: FundamentalData) -> FundamentalData:
        with self.session_factory() as session:
            session.add(fundamental_data)
            session.commit()
            session.refresh(fundamental_data)
            return fundamental_data


# class NotFoundError(Exception):

#     entity_name: str

#     def __init__(self, entity_id):
#         super().__init__(f"{self.entity_name} not found, id: {entity_id}")


# class UserNotFoundError(NotFoundError):

#     entity_name: str = "User"
