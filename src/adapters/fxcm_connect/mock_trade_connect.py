from decimal import Decimal
import json
import os
import uuid

import dotenv
from fxcmpy import fxcmpy
from pandas import DataFrame
from src.adapters.fxcm_connect.base_trade_connect import BaseTradeConnect
from src.config import ForexPairEnum, PeriodEnum, OrderTypeEnum
import pandas as pd

env = os.path.abspath(os.curdir) + "/src/.env"
config = dotenv.dotenv_values(env)


class MockTradeConnect(BaseTradeConnect):
    def __init__(self, conf: dict = None) -> None:
        """set up the connection to fxcm"""
        self.open_connection()

    async def get_connection_status(self) -> None:
        """Get the connection status"""

    async def close_connection(self) -> None:
        """Closes the connection"""

    def open_connection(self) -> None:
        """Open the connection"""

    async def get_refined_data(self, data):
        """Refine the data that we get from FXCM"""

    async def get_candle_data(
        self,
        instrument: ForexPairEnum = None,
        period: PeriodEnum = None,
        number: int = 100,
    ) -> DataFrame:
        """get the candle data for an instrument"""

        file = os.path.abspath(os.curdir) + "/test/data.json"
        with open(file, "r") as f:
            data_loaded = json.load(f)
        return await self.get_refined_data(data_loaded)

    async def get_refined_data(self, data):
        """Refine the data that we get from FXCM"""
        list_of_candles = []
        for i in data["candles"]:
            list_of_candles.append(
                {
                    "date": i["time"],
                    "open": float(i["mid"]["o"]),
                    "high": float(i["mid"]["h"]),
                    "low": float(i["mid"]["l"]),
                    "close": float(i["mid"]["c"]),
                    "volume": float(i["volume"]),
                }
            )

        return pd.DataFrame(list_of_candles)

    async def get_open_positions(self, **kwargs):
        """returns the open positions"""
        return self.con.get_open_positions()

    async def open_trade(
        self,
        instrument: ForexPairEnum,
        is_buy: bool,
        stop: float,
        limit: float,
        amount: int,
        is_pips: bool = False,
        order_type: OrderTypeEnum = OrderTypeEnum.AT_MARKET,
        time_in_force: str = "GTC",
    ):
        """
        Opens a trade postion.

        open_trade(symbol, is_buy, amount, time_in_force, order_type, rate=0, is_in_pips=True,
        limit=None, at_market=0, stop=None, trailing_step=None, account_id=None)
        """
        return str(uuid.uuid4())

    async def close_trade(self, trade_id: str, amount: int):
        """Closes the trade position"""

    async def close_all_trades(self, trade_ids: list[str]):
        """closes all open trades"""

    async def get_account_balance(self) -> str:
        """returns the account balance"""
        return "1000"

    async def get_account_details(self):
        """returns the account details"""

    async def get_latest_close(self, instrument: ForexPairEnum) -> float:
        """returns the latest close"""

    async def modify_trade(
        self, trade_id: str, stop: float, limit: float = None
    ) -> str:
        pass

    async def get_trade_state(self, trade_id: str):
        """get the trade state"""
