import datetime
from typing import Iterator
from src.classes.trade import Trade

from sqlalchemy.orm import Session

from src.models.db_connect import context
from src.repositories.base_repository import BaseRepository


class TradeRepository(BaseRepository):
    def get_all(self) -> Iterator[Trade]:
        """Get all trade objects"""
        session: Session = self.get_session()
        return session.query(Trade).all()

    def get_trade_by_trade_id(self, trade_id: str) -> Trade:
        """Get a single trade"""
        session: Session = self.get_session()
        return session.query(Trade).filter_by(trade_id=trade_id).one_or_none()
