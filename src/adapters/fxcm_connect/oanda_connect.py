import os
import dotenv
from pandas import DataFrame
from pydantic import parse_raw_as
from src.domain.schema.trades import TradesResponse
from src.domain.schema.transaction import CloseTradeResponse, OandaResponse
from src.adapters.fxcm_connect.base_trade_connect import BaseTradeConnect
from src.config import ForexPairEnum, OrderTypeEnum, PeriodEnum, SentimentEnum
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import pandas as pd
import oandapyV20.endpoints.orders as orders
from oandapyV20.endpoints.accounts import AccountDetails
from src.domain.schema.account import AccountDetails as AccountDetailsSchema
from oandapyV20.endpoints.trades import TradeClose, TradesList

env = os.path.abspath(os.curdir) + "/src/.env"
config = dotenv.dotenv_values(env)


class OandaConnect(BaseTradeConnect):
    def __init__(self, conf: dict = None) -> None:
        """set up the connection to fxcm"""
        self.token = conf["OANDA_TOKEN"] if "OANDA_TOKEN" in conf else None
        self.account_id = (
            conf["OANDA_ACCOUNT_ID"] if "OANDA_ACCOUNT_ID" in conf else None
        )

        if self.token is None:
            raise ValueError("No config defined")
        self.open_connection()

    async def get_connection_status(self) -> None:
        """Get the connection status"""
        raise NotImplementedError

    async def close_connection(self) -> None:
        """Closes the connection"""
        raise NotImplementedError

    def open_connection(self) -> None:
        """Open the connection"""
        self.client = oandapyV20.API(access_token=self.token)

    async def get_candle_data(
        self, instrument: ForexPairEnum, period: PeriodEnum, number: int = 100
    ) -> DataFrame:
        """get the candle data for an instrument"""
        instrument = instrument.value.replace("/", "_")
        params = {
            "count": number,  # Number of candles to retrieve
            "granularity": str.upper(
                period.value
            ),  # Candlestick granularity, M5 means 5 minutes
        }
        r = instruments.InstrumentsCandles(instrument="EUR_USD", params=params)
        return self.client.request(r)

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
        trades_list_endpoint = TradesList(self.account_id)
        self.client.request(trades_list_endpoint)
        trades = trades_list_endpoint.response.get("trades", [])
        trades: TradesResponse = parse_raw_as(TradesResponse, trades)
        return trades

    async def open_trade(
        self,
        instrument: ForexPairEnum,
        is_buy: bool,
        is_pips: bool,
        stop: float,
        limit: float,
        amount: int,
        order_type: OrderTypeEnum = OrderTypeEnum.MARKET,
        time_in_force: str = "GTC",
    ):
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
            }
        }

        data["order"].update(stops)

        r = orders.OrderCreate(self.account_id, data)
        response = self.client.request(r)
        response_model: OandaResponse = parse_raw_as(OandaResponse, response)
        return response_model.order_fill_transaction.id

    async def close_trade(
        self, trade_id: str, amount: int
    ) -> CloseTradeResponse:
        """closes a trade position"""
        trade_close_endpoint = TradeClose(self.account_id, trade_id)
        response = self.client.request(trade_close_endpoint)
        close_model: CloseTradeResponse = parse_raw_as(
            CloseTradeResponse, response
        )
        return close_model

    async def close_all_trades(self, trade_ids: list[str]):
        """closes all open trades"""
        for trade in trade_ids:
            await self.close_trade(trade)

    async def get_account_balance(self):
        """returns the account balance"""
        account_details = await self.get_account_details()

        return account_details.account.account.balance

    async def get_account_details(self) -> AccountDetailsSchema:
        """returns the account details"""
        account_details_endpoint = AccountDetails(self.account_id)

        response = self.client.request(account_details_endpoint)
        response: AccountDetailsSchema = parse_raw_as(
            AccountDetailsSchema, response
        )
        return response
