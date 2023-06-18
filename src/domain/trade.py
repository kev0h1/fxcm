from dataclasses import dataclass, field
from datetime import datetime
from src.config import SignalTypeEnum
from decimal import Decimal


@dataclass
class Trade:
    trade_id: int
    position_size: int
    stop: Decimal
    limit: Decimal
    is_buy: bool
    signal: SignalTypeEnum
    is_winner: bool = field(default=None)
    initiated_date: datetime = field(default=datetime.now())
