from typing import List, Optional
from pydantic import BaseModel, Field


class Trade(BaseModel):
    id: str
    instrument: str
    price: float
    open_time: str = Field(alias="openTime")
    state: str
    initial_units: str = Field(alias="initialUnits")
    initial_margin_required: str = Field(alias="initialMarginRequired")
    # Add any additional fields here...


class TradesResponse(BaseModel):
    trades: List[Trade]
    last_transaction_id: str = Field(alias="lastTransactionID")
