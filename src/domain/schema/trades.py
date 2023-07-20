from typing import List
from pydantic import BaseModel


class StopLossOrder(BaseModel):
    id: str
    createTime: str
    type: str
    tradeID: str
    price: str
    timeInForce: str
    triggerCondition: str
    triggerMode: str
    state: str


class TradeInfo(BaseModel):
    id: str
    instrument: str
    price: str
    openTime: str
    initialUnits: str
    initialMarginRequired: str
    state: str
    currentUnits: str
    realizedPL: str
    financing: str
    dividendAdjustment: str
    unrealizedPL: str
    marginUsed: str
    stopLossOrder: StopLossOrder


class TradeList(BaseModel):
    trades: List[TradeInfo]
