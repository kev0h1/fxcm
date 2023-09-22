import os
import dotenv
from pandas import DataFrame
from pydantic import parse_obj_as
from src.domain.schema.trades import (
    TradeInfo,
    TradeCRDCOSchema,
    StopLossOrder,
)
from src.domain.schema.transaction import OrderSchema, OrderTransaction
from src.adapters.fxcm_connect.base_trade_connect import BaseTradeConnect
from src.config import ForexPairEnum, OrderTypeEnum, PeriodEnum
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import pandas as pd
import oandapyV20.endpoints.orders as orders
from oandapyV20.endpoints.accounts import AccountDetails
from src.domain.schema.account import AccountDetailsSchema
from oandapyV20.endpoints.trades import (
    TradeClose,
    TradesList,
    TradeCRCDO,
)

from oandapyV20.exceptions import V20Error


from src.logger import get_logger
from src.utils import get_secret

logger = get_logger(__name__)


def error_handler(func):
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except V20Error as e:
            logger.error(e)
            raise e

    return wrapper


class OandaConnect(BaseTradeConnect):
    def __init__(self) -> None:
        """set up the connection to fxcm"""

        if os.environ.get("DEPLOY_ENV", "local") == "aws":
            secret = get_secret("OandaSecret")
            self.token, self.account_id = (
                secret["OANDA_TOKEN"],
                secret["OANDA_ACCOUNT_ID"],
            )
        else:
            self.token = os.environ["OANDA_TOKEN"]
            self.account_id = os.environ["OANDA_ACCOUNT_ID"]

        if self.token is None:
            raise ValueError("No config defined")
        self.open_connection()

    @error_handler
    async def get_connection_status(self) -> None:
        """Get the connection status"""
        raise NotImplementedError

    @error_handler
    async def close_connection(self) -> None:
        """Closes the connection"""
        raise NotImplementedError

    def open_connection(self) -> None:
        """Open the connection"""
        self.client = oandapyV20.API(access_token=self.token)

    @error_handler
    async def get_candle_data(
        self, instrument: ForexPairEnum, period: PeriodEnum, number: int = 100
    ) -> dict:
        """get the candle data for an instrument"""
        instrument = instrument.value.replace("/", "_")
        params = {
            "count": number,  # Number of candles to retrieve
            "granularity": str.upper(
                period.value
            ),  # Candlestick granularity, M5 means 5 minutes
        }
        r = instruments.InstrumentsCandles(
            instrument=instrument, params=params
        )
        return await self.get_refined_data(self.client.request(r))

    @error_handler
    async def get_refined_data(self, data) -> DataFrame:
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

    @error_handler
    async def get_open_positions(self, **kwargs) -> list[TradeInfo]:
        """returns the open positions"""
        trades_list_endpoint = TradesList(self.account_id)
        self.client.request(trades_list_endpoint)
        trades = trades_list_endpoint.response.get("trades", [])
        retrieved_trades = []
        for trade in trades:
            retrieved_trades.append(parse_obj_as(TradeInfo, trade))

        logger.info(
            "Retrieved open positions %s"
            % ", ".join(
                [retrieved_trade.id for retrieved_trade in retrieved_trades]
            )
        )
        return trades

    @error_handler
    async def open_trade(
        self,
        instrument: ForexPairEnum,
        is_buy: bool,
        stop: float,
        limit: float,
        amount: int,
        is_pips: bool = False,
        order_type: OrderTypeEnum = OrderTypeEnum.MARKET,
        time_in_force: str = "GTC",
    ) -> str:
        """
        Opens a trade postion.

        open_trade(symbol, is_buy, amount, time_in_force, order_type, rate=0, is_in_pips=True,
        limit=None, at_market=0, stop=None, trailing_step=None, account_id=None)
        """
        if is_buy:
            amount = amount
        else:
            amount = -amount

        stops = {}
        if limit is not None:
            stops["takeProfitOnFill"] = {"price": str(limit)}
        if stop is not None:
            stops["stopLossOnFill"] = {
                "timeInForce": time_in_force,
                "price": str(stop),
            }

        data = {
            "order": {
                "instrument": instrument.value.replace("/", "_"),
                "units": str(amount),
                "type": order_type.value,
                "positionFill": "DEFAULT",
                "timeInForce": "FOK",  # added this
                # "priceBound": "1.12",  # added this
            }
        }

        data["order"].update(stops)

        r = orders.OrderCreate(self.account_id, data)
        response = self.client.request(r)
        response_model: OrderSchema = parse_obj_as(OrderSchema, response)
        if response_model.orderFillTransaction is not None:
            logger.info(
                "Opened trade %s for %s units for currency pair %s, with a stop of %s"
                % (
                    response_model.orderFillTransaction.id,
                    amount,
                    instrument,
                    stop,
                )
            )
            return response_model.orderFillTransaction.id
        else:
            if response_model.orderCancelTransaction is not None:
                reason = response_model.orderCancelTransaction.reason
            else:
                reason = "unable to establish reason"

            logger.error(
                "Failed to open trade for %s units for currency pair %s, with a stop of %s. The reason was %s"
                % (amount, instrument, stop, reason)
            )

    @error_handler
    async def close_trade(
        self, trade_id: str, amount: int
    ) -> tuple[str, float]:
        """closes a trade position"""
        trade_close_endpoint = TradeClose(self.account_id, trade_id)
        response = self.client.request(trade_close_endpoint)
        response_model: OrderSchema = parse_obj_as(OrderSchema, response)
        if response_model.orderFillTransaction is not None:
            return response_model.orderFillTransaction.id, float(
                response_model.orderFillTransaction.pl
            )
        else:
            if response_model.orderCancelTransaction is not None:
                reason = response_model.orderCancelTransaction.reason
            else:
                reason = "unable to establish reason"

            logger.error(
                "Failed to close trade for id %s. The reason was %s"
                % (trade_id, reason)
            )
        return None, None

    @error_handler
    async def close_all_trades(self, trade_ids: list[str]):
        """closes all open trades"""
        for trade in trade_ids:
            await self.close_trade(trade)

    @error_handler
    async def get_account_balance(self) -> str:
        """returns the account balance"""
        account_details = await self.get_account_details()

        return account_details.account.balance

    @error_handler
    async def get_account_details(self) -> AccountDetailsSchema:
        """returns the account details"""
        account_details_endpoint = AccountDetails(self.account_id)

        response = self.client.request(account_details_endpoint)
        response: AccountDetailsSchema = parse_obj_as(
            AccountDetailsSchema, response
        )
        return response

    @error_handler
    async def get_latest_close(self, instrument: ForexPairEnum) -> float:
        """returns the latest close"""
        data: DataFrame = await self.get_candle_data(
            instrument, PeriodEnum.MINUTE_1, 1
        )
        return float(data.iloc[-1]["close"])

    @error_handler
    async def modify_trade(
        self, trade_id: str, stop: float, limit: float = None
    ) -> str:
        data = {
            "stopLoss": {
                "price": str(stop),
                "timeInForce": "GTC",
                "clientExtensions": {
                    "id": "StopLossOrder",
                    "tag": "strategy",
                    "comment": "New stop loss price",
                },
            }
        }
        logger.info("Modifying trade %s" % trade_id)
        trade_modify_request = TradeCRCDO(
            accountID=self.account_id, tradeID=trade_id, data=data
        )
        response = self.client.request(trade_modify_request)
        response_model: TradeCRDCOSchema = parse_obj_as(
            TradeCRDCOSchema, response
        )
        return response_model

    @error_handler
    async def get_trade_state(self, trade_id: str):
        """get the trade state"""
        trades = []
        r = TradesList(
            self.account_id,
            params={
                "state": "OPEN",
            },
        )
        rv = self.client.request(r)
        trades.extend(rv["trades"])
        r = TradesList(
            self.account_id,
            params={
                "state": "CLOSED",
            },
        )
        rv = self.client.request(r)
        trades.extend(rv["trades"])
        for trade in trades:
            if trade["id"] == trade_id:
                logger.info("Getting trade details for %s" % trade_id)
                return trade["state"], float(trade["realizedPL"])

        return None, None

    @error_handler
    async def get_pending_orders(self) -> list[StopLossOrder]:
        r = orders.OrderList(self.account_id)

        # Send the request
        response = self.client.request(r)

        # Extract and display pending orders
        pending_orders = response["orders"]
        pending_orders = parse_obj_as(list[StopLossOrder], pending_orders)
        return pending_orders

    @error_handler
    async def cancel_pending_order(self, order_id: str):
        r = orders.OrderCancel(self.account_id, order_id)
        response = self.client.request(r)
        response_model: OrderTransaction = parse_obj_as(
            OrderTransaction, response["orderCancelTransaction"]
        )
        return response_model
