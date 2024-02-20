from pydantic import BaseModel
from typing import List, Optional


class StopLossOnFill(BaseModel):
    price: str
    timeInForce: str
    triggerMode: str


class TradeOpened(BaseModel):
    price: str
    tradeID: str
    units: str
    guaranteedExecutionFee: str
    quoteGuaranteedExecutionFee: str
    halfSpreadCost: str
    initialMarginRequired: str


class Bid(BaseModel):
    price: str
    liquidity: str


class Ask(BaseModel):
    price: str
    liquidity: str


class FullPrice(BaseModel):
    closeoutBid: str
    closeoutAsk: str
    timestamp: str
    bids: List[Bid]
    asks: List[Ask]


class ConversionFactor(BaseModel):
    factor: str


class HomeConversionFactors(BaseModel):
    gainQuoteHome: ConversionFactor
    lossQuoteHome: ConversionFactor
    gainBaseHome: ConversionFactor
    lossBaseHome: ConversionFactor


class OrderTransaction(BaseModel):
    id: str
    accountID: str
    userID: int
    batchID: str
    requestID: str
    time: str
    type: str
    instrument: Optional[str]
    units: Optional[str]
    priceBound: Optional[str]
    timeInForce: Optional[str]
    positionFill: Optional[str]
    stopLossOnFill: Optional[StopLossOnFill]
    reason: str
    orderID: Optional[str]


class OrderFillTransaction(BaseModel):
    id: str
    accountID: str
    userID: int
    batchID: str
    requestID: str
    time: str
    type: str
    orderID: str
    instrument: str
    units: str
    requestedUnits: str
    price: str
    pl: str
    quotePL: str
    financing: str
    baseFinancing: str
    commission: str
    accountBalance: str
    gainQuoteHomeConversionFactor: str
    lossQuoteHomeConversionFactor: str
    guaranteedExecutionFee: str
    quoteGuaranteedExecutionFee: str
    halfSpreadCost: str
    fullVWAP: str
    reason: str
    fullPrice: FullPrice
    homeConversionFactors: HomeConversionFactors


class OrderSchema(BaseModel):
    orderCreateTransaction: OrderTransaction
    orderFillTransaction: Optional[OrderFillTransaction]
    orderCancelTransaction: Optional[OrderTransaction]
    relatedTransactionIDs: List[str]
    lastTransactionID: str
