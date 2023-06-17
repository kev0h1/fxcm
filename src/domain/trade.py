from dataclasses import dataclass
from datetime import datetime
from src.config import SignalTypeEnum
from mongoengine import *


class Trade(Document):
    def __init__(
        self,
        trade_id,
        position_size,
        stop,
        limit,
        is_buy,
        signal,
        *args,
        **values
    ):
        super().__init__(*args, **values)
        self.trade_id = trade_id
        self.position_size = position_size
        self.stop = stop
        self.limit = limit
        self.is_buy = is_buy
        self.signal = signal

    trade_id = IntField(primary_key=True)
    position_size = IntField()
    stop = FloatField()
    limit = FloatField()
    is_buy = BooleanField()
    signal = EnumField(SignalTypeEnum)
    is_winner = BooleanField(default=False)
    initiated_date = DateTimeField(default=datetime.now())
