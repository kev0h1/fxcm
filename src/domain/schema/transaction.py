from pydantic import BaseModel, Field
from typing import List, Optional
import re


def to_camel(string: str) -> str:
    string = re.sub("(?<=[a-z])(?=[A-Z])", "_", string).lower()
    return string


class Transaction(BaseModel):
    type: str = Field(alias="type")
    instrument: str = Field(alias="instrument")
    units: str = Field(alias="units")
    time_in_force: str = Field(alias="timeInForce")
    position_fill: str = Field(alias="positionFill")
    reason: str = Field(alias="reason")
    id: str = Field(alias="id")
    account_id: str = Field(alias="accountID")
    user_id: int = Field(alias="userID")
    batch_id: str = Field(alias="batchID")
    request_id: str = Field(alias="requestID")
    time: str = Field(alias="time")
    price: str = Field(alias="price", default=None)
    pl: str = Field(alias="pl", default=None)
    financing: str = Field(alias="financing", default=None)
    commission: str = Field(alias="commission", default=None)
    account_balance: str = Field(alias="accountBalance", default=None)
    gain_quote_home_conversion_factor: str = Field(
        alias="gainQuoteHomeConversionFactor", default=None
    )
    loss_quote_home_conversion_factor: str = Field(
        alias="lossQuoteHomeConversionFactor", default=None
    )
    guaranteed_execution_fee: str = Field(
        alias="guaranteedExecutionFee", default=None
    )
    half_spread_cost: str = Field(alias="halfSpreadCost", default=None)
    full_vwap: str = Field(alias="fullVWAP", default=None)
    order_id: str = Field(alias="orderID", default=None)

    class Config:
        allow_population_by_field_name = True
        alias_generator = to_camel


class OandaResponse(BaseModel):
    order_create_transaction: Transaction = Field(
        alias="orderCreateTransaction"
    )
    order_fill_transaction: Transaction = Field(alias="orderFillTransaction")
    related_transaction_i_ds: List[str] = Field(alias="relatedTransactionIDs")
    last_transaction_id: str = Field(alias="lastTransactionID")

    class Config:
        allow_population_by_field_name = True
        alias_generator = to_camel


class TradeClose(BaseModel):
    trade_id: str = Field(alias="tradeID")
    units: str
    price: Optional[float]


class OrderCreateTransaction(BaseModel):
    type: str
    instrument: str
    units: str
    time_in_force: str = Field(alias="timeInForce")
    position_fill: str = Field(alias="positionFill")
    reason: str
    id: str
    account_id: str = Field(alias="accountID")
    user_id: str = Field(alias="userID")
    batch_id: str = Field(alias="batchID")
    request_id: str = Field(alias="requestID")
    time: str
    trade_close: Optional[TradeClose] = Field(alias="tradeClose")


class OrderFillTransaction(BaseModel):
    type: str
    order_id: str = Field(alias="orderID")
    instrument: str
    units: str
    price: str
    pl: str
    financing: str
    commission: str
    account_balance: str = Field(alias="accountBalance")
    id: str
    account_id: str = Field(alias="accountID")
    user_id: str = Field(alias="userID")
    batch_id: str = Field(alias="batchID")
    request_id: str = Field(alias="requestID")
    time: str


class CloseTradeResponse(BaseModel):
    order_create_transaction: OrderCreateTransaction = Field(
        alias="orderCreateTransaction"
    )
    order_fill_transaction: OrderFillTransaction = Field(
        alias="orderFillTransaction"
    )
    related_transaction_ids: list[str] = Field(alias="relatedTransactionIDs")
    last_transaction_id: str = Field(alias="lastTransactionID")
