from typing import List, Optional, Union
from pydantic import BaseModel
from datetime import datetime


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


class TransactionDetails(BaseModel):
    id: str
    accountID: str
    userID: int
    batchID: str
    requestID: str
    time: datetime
    type: str


class StopLossOrderCancelTransaction(TransactionDetails):
    orderID: Optional[str]
    clientOrderID: Optional[str]


class StopLossOrderTransaction(TransactionDetails):
    tradeID: str
    timeInForce: str


class TradeCRDCOSchema(BaseModel):
    stopLossOrderCancelTransaction: Optional[StopLossOrderCancelTransaction]
    stopLossOrderTransaction: StopLossOrderTransaction
    relatedTransactionIDs: List[str]
    lastTransactionID: str


class NotFoundTrade(BaseModel):
    tradeID: str
    rejectReason: str


class NotFoundResponse(BaseModel):
    tradeNotFound: Optional[NotFoundTrade]
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
    realizedPL: Optional[str]
    unrealizedPL: Optional[str]
    averageClosePrice: Optional[str]
    stopLossOrder: StopLossOrder


class OpenTradeResponse(BaseModel):
    trade: OpenTrade
    lastTransactionID: str


TradeDetailResponse = Union[OpenTradeResponse, NotFoundResponse]
