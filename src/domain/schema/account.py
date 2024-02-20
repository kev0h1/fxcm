from typing import List, Optional
from pydantic import BaseModel


class Account(BaseModel):
    guaranteedStopLossOrderMode: str
    hedgingEnabled: bool
    id: str
    createdTime: str
    currency: str
    createdByUserID: int
    alias: str
    marginRate: str
    lastTransactionID: str
    balance: str
    openTradeCount: int
    openPositionCount: int
    pendingOrderCount: int
    pl: str
    resettablePL: str
    resettablePLTime: str
    financing: str
    commission: str
    dividendAdjustment: str
    guaranteedExecutionFees: str
    orders: List
    positions: List
    trades: List
    unrealizedPL: str
    NAV: str
    marginUsed: str
    marginAvailable: str
    positionValue: str
    marginCloseoutUnrealizedPL: str
    marginCloseoutNAV: str
    marginCloseoutMarginUsed: str
    marginCloseoutPositionValue: str
    marginCloseoutPercent: str
    withdrawalLimit: str
    marginCallMarginUsed: str
    marginCallPercent: str


class AccountDetailsSchema(BaseModel):
    account: Account
    lastTransactionID: str
