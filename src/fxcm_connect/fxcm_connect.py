from decimal import Decimal
import os

import dotenv
from fxcmpy import fxcmpy
from pandas import DataFrame
from src.classes.trade import Trade
from sqlalchemy.orm import Session
from src.config import ForexPairEnum, PeriodEnum, OrderTypeEnum
from src.container.container import Container
from src.errors.errors import InvalidTradeParameter, NoStopDefinedException
from src.repositories.trade_repository import TradeRepository
from dependency_injector.wiring import inject, Provide
from fastapi import Depends

env = os.path.abspath(os.curdir) + "/src/.env"
config = dotenv.dotenv_values(env)


class FXCMConnect:
    def __init__(self, conf: dict) -> None:
        """set up the connection to fxcm"""
        self.token = conf["TOKEN"] if "TOKEN" in conf else None

        if self.token is None:
            raise ValueError("No config defined")
        self.open_connection()

    def get_connection_status(self) -> None:
        """Get the connection status"""
        return self.con.is_connected()

    def close_connection(self) -> None:
        """Closes the connection"""
        self.con.close()

    def open_connection(self) -> None:
        """Open the connection"""

        self.con = fxcmpy(
            access_token=self.token,
            log_level="error",
        )

    def get_candle_data(
        self, instrument: ForexPairEnum, period: PeriodEnum, number: int = 100
    ) -> DataFrame:
        """get the candle data for an instrument"""
        return self.con.get_candles(
            instrument=instrument.value, period=period.value, number=number
        )

    def get_open_positions(self, **kwargs):
        """returns the open positions"""
        return self.con.get_open_positions()

    def open_trade(
        self,
        session: Session,
        instrument: ForexPairEnum,
        is_buy: bool,
        is_pips: bool,
        stop: float,
        limit: float,
        amount: int,
        order_type: OrderTypeEnum = OrderTypeEnum.AT_MARKET,
        time_in_force: str = "GTC",
    ):
        """
        Opens a trade postion.

        open_trade(symbol, is_buy, amount, time_in_force, order_type, rate=0, is_in_pips=True,
        limit=None, at_market=0, stop=None, trailing_step=None, account_id=None)"""
        stops = {}
        if limit is not None:
            stops["limit"] = limit
        if stop is not None:
            stops["stop"] = stop

        self.validate_stops(is_buy, is_pips, stop, limit)

        self.con.open_trade(
            symbol=instrument.value,
            is_buy=is_buy,
            is_in_pips=is_pips,
            amount=amount,
            time_in_force=time_in_force,
            order_type=order_type.value,
            **stops
        )
        self.create_trade_obj(session)

    def validate_stops(self, is_buy, is_pips, stop, limit):
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

    @inject
    def create_trade_obj(
        self,
        trade_repository: TradeRepository = Depends(
            Provide[Container.fundamental_data_repository]
        ),
    ):
        """Creates the trade object"""
        fxcm_postion = self.get_open_positions()
        trade_id = fxcm_postion.iloc[-1]["tradeId"]
        if not trade_repository.get_trade_by_trade_id(trade_id=trade_id):
            trade = Trade(
                trade_id=trade_id,
                position_size=fxcm_postion["amountK"],
                stop=fxcm_postion["stop"],
                limit=fxcm_postion["limit"],
                is_buy=fxcm_postion["isBuy"],
            )
            trade_repository.add(trade)

    def close_trade(self, trade_id: str, amount: int):
        """Closes the trade position"""
        self.con.close_trade(trade_id=trade_id, amount=amount)
