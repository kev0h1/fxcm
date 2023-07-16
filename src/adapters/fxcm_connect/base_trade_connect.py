from abc import ABC, abstractmethod

from pandas import DataFrame
from src.config import ForexPairEnum, OrderTypeEnum, PeriodEnum

from src.domain.errors.errors import InvalidTradeParameter


class BaseTradeConnect(ABC):
    @abstractmethod
    async def get_connection_status(self) -> None:
        """Get the connection status"""
        raise NotImplementedError

    @abstractmethod
    async def close_connection(self) -> None:
        """Closes the connection"""
        raise NotImplementedError

    @abstractmethod
    def open_connection(self) -> None:
        """Open the connection"""
        raise NotImplementedError

    @abstractmethod
    async def get_candle_data(
        self,
        instrument: ForexPairEnum,
        period: PeriodEnum,
        number: int = 100,
        get_refined_data: bool = True,
    ) -> DataFrame:
        """get the candle data for an instrument"""
        raise NotImplementedError

    @abstractmethod
    async def get_open_positions(self, **kwargs):
        """returns the open positions"""
        raise NotImplementedError

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

    @abstractmethod
    async def close_trade(self, trade_id: str, amount: int):
        """Closes the trade position"""
        raise NotImplementedError

    @abstractmethod
    async def get_refined_data(self, data):
        """Refine the data that we get from FXCM"""

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
    ) -> str:
        raise NotImplementedError

    async def get_account_balance(self) -> str:
        """returns the account balance"""
        raise NotImplementedError

    async def get_account_details(self) -> str:
        """returns the account details"""
        raise NotImplementedError
