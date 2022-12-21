from decimal import Decimal
import os

import dotenv
from fxcmpy import fxcmpy
from pandas import DataFrame

from src.config import ForexPairEnum, PeriodEnum, OrderTypeEnum
from src.errors.errors import NoStopDefinedException

env = os.path.abspath(os.curdir) + "/src/.env"
config = dotenv.dotenv_values(env)


class FXCMConnect:
    def __init__(self, conf: dict) -> None:
        """set up the connection to fxcm"""
        token = conf["TOKEN"] if "TOKEN" in conf else None

        if token is None:
            raise ValueError("No config defined")
        self.con = fxcmpy(
            access_token=token or conf["TOKEN"], log_level="error"
        )

    def get_candle_data(
        self, instrument: ForexPairEnum, period: PeriodEnum, number: int = 100
    ) -> DataFrame:
        """get the candle data for an instrument"""
        return self.con.get_candles(
            instrument=instrument.value, period=period.value, number=number
        )

    def open_trade(
        self,
        instrument: ForexPairEnum,
        is_buy: bool,
        is_pips: bool,
        stop: Decimal,
        limit: Decimal,
        amount: Decimal,
        order_type: OrderTypeEnum = OrderTypeEnum.AT_MARKET,
        time_in_force: str = "GTC",
    ):
        """
        Opens a trade postion.

        open_trade(symbol, is_buy, amount, time_in_force, order_type, rate=0, is_in_pips=True,
        limit=None, at_market=0, stop=None, trailing_step=None, account_id=None)"""
        stops = {}
        if limit:
            stops["limit"] = limit
        if stop:
            stops["stop"] = stop

        if not limit and not stop:
            raise NoStopDefinedException()

        trade = self.con.open_trade(
            symbol=instrument.value,
            is_buy=is_buy,
            is_in_pips=is_pips,
            amount=amount,
            time_in_force=time_in_force,
            order_type=order_type,
            **stops
        )
