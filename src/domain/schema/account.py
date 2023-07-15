from pydantic import BaseModel, Field
from typing import Optional


class Account(BaseModel):
    id: str = Field(alias="id")
    alias: str = Field(alias="alias")
    currency: str = Field(alias="currency")
    balance: str = Field(alias="balance")
    created_by_user_id: int = Field(alias="createdByUserID")
    created_time: str = Field(alias="createdTime")


class AccountDetailsResponse(BaseModel):
    account: Account
    last_transaction_id: str = Field(alias="lastTransactionID")


class AccountDetails(BaseModel):
    account_id: str = Field(alias="accountID")
    status: str = Field(alias="status")
    account: Optional[AccountDetailsResponse] = None
