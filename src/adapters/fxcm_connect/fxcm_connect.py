from decimal import Decimal
import os

import dotenv
from fxcmpy import fxcmpy
from pandas import DataFrame
from src.adapters.fxcm_connect.base_trade_connect import BaseTradeConnect
from src.config import ForexPairEnum, PeriodEnum, OrderTypeEnum
from src.domain.errors.errors import (
    InvalidTradeParameter,
)


env = os.path.abspath(os.curdir) + "/src/.env"
config = dotenv.dotenv_values(env)


class FXCMConnect(BaseTradeConnect):
    def __init__(self, conf: dict) -> None:
        """set up the connection to fxcm"""
        self.token = conf["TOKEN"] if "TOKEN" in conf else None

        if self.token is None:
            raise ValueError("No config defined")
        self.open_connection()

    async def get_connection_status(self) -> None:
        """Get the connection status"""
        return self.con.is_connected()

    async def close_connection(self) -> None:
        """Closes the connection"""
        self.con.close()

    def open_connection(self) -> None:
        """Open the connection"""

        self.con = fxcmpy(
            access_token=self.token,
            log_level="error",
        )

    async def get_candle_data(
        self,
        instrument: ForexPairEnum,
        period: PeriodEnum,
        number: int = 100,
        get_refined_data: bool = True,
    ) -> DataFrame:
        """get the candle data for an instrument"""
        data = self.con.get_candles(
            instrument=instrument.value, period=period.value, number=number
        )
        if get_refined_data:
            return await self.get_refined_data(data)
        return data

    async def get_refined_data(self, data):
        """Refine the data that we get from FXCM"""
        data.drop(
            ["bidopen", "bidclose", "bidhigh", "bidlow"], inplace=True, axis=1
        )
        data.rename(
            columns={
                "askopen": "open",
                "askclose": "close",
                "askhigh": "high",
                "asklow": "low",
                "tickqty": "volume",
            },
            inplace=True,
        )
        return data

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
        stops = {}
        if limit is not None:
            stops["limit"] = limit
        if stop is not None:
            stops["stop"] = stop

        await self.validate_stops(is_buy, is_pips, stop, limit)

        self.con.open_trade(
            symbol=instrument.value,
            is_buy=is_buy,
            is_in_pips=is_pips,
            amount=amount,
            time_in_force=time_in_force,
            order_type=order_type.value,
            **stops
        )
        # TODO add create trade clean up

    async def validate_stops(self, is_buy, is_pips, stop, limit):
        """Validates the stops and limits"""
        if not stop:
            raise InvalidTradeParameter("no stop defined")

        if is_pips:
            if limit < 0:
                raise InvalidTradeParameter(
                    "limit must be greated than 0 for trades when using pips"
                )
            if stop > 0:
                raise InvalidTradeParameter(
                    "stop must be less than 0 for trades when using pips"
                )
        else:
            if (
                is_buy
                and limit is not None
                and stop is not None
                and limit < stop
            ):
                raise InvalidTradeParameter(
                    "limit must be greater for buy trades"
                )
            if (
                not is_buy
                and limit is not None
                and stop is not None
                and limit > stop
            ):
                raise InvalidTradeParameter(
                    "limit must be less than stop for sell trade"
                )

    async def close_trade(self, trade_id: str, amount: int):
        """Closes the trade position"""
        self.con.close_trade(trade_id=trade_id, amount=amount)
