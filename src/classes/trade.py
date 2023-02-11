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
