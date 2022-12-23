from dataclasses import dataclass, field
from datetime import datetime
from sqlalchemy.orm import Session
from src.config import SignalTypeEnum


@dataclass
class Trade:
    trade_id: int
    position_size: int
    stop: float
    limit: float
    is_buy: bool
    signal: SignalTypeEnum = field(default=SignalTypeEnum.MOVING_AVERAGE)
    is_winner: bool = field(default=None)
    initiated_date: datetime = field(default=datetime.now())

    @classmethod
    def get_trades(cls, session: Session, **kwargs):
        """Get trades"""
        return session.query(cls).filter_by(**kwargs).all()

    @classmethod
    def get_trade_by_trade_id(cls, session: Session, trade_id: str):
        """Get trades by trade id"""
        return session.query(cls).filter_by(trade_id=trade_id).one_or_none()
