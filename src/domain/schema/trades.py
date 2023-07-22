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


class OrderTransaction(BaseModel):
    orderID: str
    batchID: str
    reason: str
    time: str
    type: str
    userID: int
    id: str
    accountID: str
    replacedByOrderID: str = None
    tradeID: str = None
    price: str = None
    timeInForce: str = None
    triggerCondition: str = None
    replacesOrderID: str = None
    cancellingTransactionID: str = None


class TakeProfitOrderTransaction(BaseModel):
    tradeID: str
    price: str
    timeInForce: str
    reason: str
    id: str
    batchID: str
    triggerCondition: str
    userID: int
    time: str
    type: str
    accountID: str


class TradeCRDCOSchema(BaseModel):
    lastTransactionID: str
    stopLossOrderCancelTransaction: OrderTransaction
    stopLossOrderTransaction: OrderTransaction
    relatedTransactionIDs: List[str]
    takeProfitOrderTransaction: TakeProfitOrderTransaction


from typing import Union, List
from pydantic import BaseModel


class NotFoundTrade(BaseModel):
    tradeID: str
    rejectReason: str


class NotFoundResponse(BaseModel):
    tradeNotFound: NotFoundTrade
    lastTransactionID: str


class StopLossOrder(BaseModel):
    id: str
    createTime: str
    state: str
    triggerCondition: str
    price: str


class OpenTrade(BaseModel):
    id: str
    instrument: str
    price: str
    openTime: str
    state: str
    initialUnits: str
    currentUnits: str
    realizedPL: str
    unrealizedPL: str
    averageClosePrice: str
    stopLossOrder: StopLossOrder


class OpenTradeResponse(BaseModel):
    trade: OpenTrade
    lastTransactionID: str


TradeDetailResponse = Union[OpenTradeResponse, NotFoundResponse]
