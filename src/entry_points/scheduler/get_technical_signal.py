from src.container.container import Container

from src.service_layer.indicators import Indicators
from src.service_layer.uow import MongoUnitOfWork

from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.config import ForexPairEnum, PeriodEnum, SentimentEnum

from src.domain.events import (
    CloseForexPairEvent,
    OpenTradeEvent,
)
from src.logger import get_logger
import pandas as pd

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
logger = get_logger(__name__)


@inject
async def get_technical_signal(
    uow: MongoUnitOfWork = Depends(Provide[Container.uow]),
    indicator: Indicators = Depends(Provide[Container.indicator_service]),
) -> None:  # type: ignore
    """Gets the technical signal for the currency"""
    async with uow:
        for forex_pair in ForexPairEnum.__members__.values():
            refined_data: pd.DataFrame = (
                await uow.fxcm_connection.get_candle_data(
                    instrument=ForexPairEnum(forex_pair),
                    period=PeriodEnum.MINUTE_5,
                    number=250,
                )
            )

            refined_data = await indicator.get_simple_moving_average(
                refined_data,
                period=10,
                col="close",
                column_name="ShortTerm_MA",
            )

            refined_data = await indicator.get_macd(refined_data, "close")

            refined_data = await indicator.get_rsi(refined_data, period=14)

            refined_data = await indicator.get_atr(refined_data, period=14)

            refined_data["Prev_ShortTerm_MA"] = refined_data[
                "ShortTerm_MA"
            ].shift(1)

            refined_data["prev_close"] = refined_data["close"].shift(1)

            refined_data["prev_rsi"] = refined_data["rsi"].shift(1)

            refined_data["prev_macd"] = refined_data["macd"].shift(1)
            refined_data["prev_macd_h"] = refined_data["macd_h"].shift(1)
            refined_data["prev_macd_s"] = refined_data["macd_s"].shift(1)

            refined_data = await get_signal(refined_data)
            if refined_data.iloc[-1]["Signal"] > 0:
                logger.warning("Bullish Signal generated for %s" % forex_pair)
                await uow.publish(
                    CloseForexPairEvent(
                        forex_pair=forex_pair, sentiment=SentimentEnum.BEARISH
                    )
                )
                await uow.publish(
                    OpenTradeEvent(
                        forex_pair=forex_pair,
                        sentiment=SentimentEnum.BULLISH,
                        stop=refined_data.iloc[-1]["ATR_Stop"],
                        close=refined_data.iloc[-1]["close"],
                    )
                )
            elif refined_data.iloc[-1]["Signal"] < 0:
                logger.warning("Bearish Signal generated for %s" % forex_pair)
                await uow.publish(
                    CloseForexPairEvent(
                        forex_pair=forex_pair, sentiment=SentimentEnum.BULLISH
                    )
                )
                await uow.publish(
                    OpenTradeEvent(
                        forex_pair=forex_pair,
                        sentiment=SentimentEnum.BEARISH,
                        stop=refined_data.iloc[-1]["ATR_Stop"],
                        close=refined_data.iloc[-1]["close"],
                    )
                )


async def get_signal(refined_data: pd.DataFrame) -> pd.DataFrame:
    # Buy Signal Conditions
    condition_close_above_MA = (
        refined_data["close"] > refined_data["ShortTerm_MA"]
    )
    condition_macd_above_signal = refined_data["macd"] > refined_data["macd_s"]
    condition_rsi_above_35 = refined_data["rsi"] > 35

    condition_close_below_MA_previous = (
        refined_data["prev_close"] < refined_data["Prev_ShortTerm_MA"]
    )
    condition_macd_below_signal_previous = (
        refined_data["prev_macd"] < refined_data["prev_macd_s"]
    )
    condition_rsi_below_35_previous = refined_data["prev_rsi"] < 35

    # Sell Signal Conditions
    condition_close_below_MA = (
        refined_data["close"] < refined_data["ShortTerm_MA"]
    )
    condition_macd_below_signal = refined_data["macd"] < refined_data["macd_s"]
    condition_rsi_below_65 = (
        refined_data["rsi"] < 65
    )  # Assuming you want to use 65 here

    condition_close_above_MA_previous = (
        refined_data["prev_close"] > refined_data["Prev_ShortTerm_MA"]
    )
    condition_macd_above_signal_previous = (
        refined_data["prev_macd"] > refined_data["prev_macd_s"]
    )
    condition_rsi_above_65_previous = (
        refined_data["prev_rsi"] > 65
    )  # Assuming you want to use 65 here

    window_size = 3  # Number of candles for sequential confirmation

    # For Buy Signals
    rolling_close_above_MA = condition_close_above_MA.rolling(
        window_size
    ).sum()
    rolling_macd_above_signal = condition_macd_above_signal.rolling(
        window_size
    ).sum()
    rolling_rsi_above_35 = condition_rsi_above_35.rolling(window_size).sum()

    rolling_close_below_MA_previous = (
        condition_close_below_MA_previous.rolling(window_size).sum()
    )
    rolling_macd_below_signal_previous = (
        condition_macd_below_signal_previous.rolling(window_size).sum()
    )
    rolling_rsi_below_35_previous = condition_rsi_below_35_previous.rolling(
        window_size
    ).sum()

    # For Sell Signals
    rolling_close_below_MA = condition_close_below_MA.rolling(
        window_size
    ).sum()
    rolling_macd_below_signal = condition_macd_below_signal.rolling(
        window_size
    ).sum()
    rolling_rsi_below_65 = condition_rsi_below_65.rolling(window_size).sum()

    rolling_close_above_MA_previous = (
        condition_close_above_MA_previous.rolling(window_size).sum()
    )
    rolling_macd_above_signal_previous = (
        condition_macd_above_signal_previous.rolling(window_size).sum()
    )
    rolling_rsi_above_65_previous = condition_rsi_above_65_previous.rolling(
        window_size
    ).sum()

    # For Buy Signal
    refined_data["Buy_Signal"] = (
        (rolling_close_above_MA > 0)
        & (rolling_macd_above_signal > 0)
        & (rolling_rsi_above_35 > 0)
        & (rolling_close_below_MA_previous > 0)
        & (rolling_macd_below_signal_previous > 0)
        & (rolling_rsi_below_35_previous > 0)
    )

    # For Sell Signal
    refined_data["Sell_Signal"] = (
        (rolling_close_below_MA > 0)
        & (rolling_macd_below_signal > 0)
        & (rolling_rsi_below_65 > 0)
        & (rolling_close_above_MA_previous > 0)
        & (rolling_macd_above_signal_previous > 0)
        & (rolling_rsi_above_65_previous > 0)
    )

    # Combine the Buy_Signal and Sell_Signal into a single Signal column
    refined_data["Signal"] = refined_data["Buy_Signal"].replace(
        {True: 1, False: 0}
    ) - refined_data["Sell_Signal"].replace({True: 1, False: 0})

    refined_data = refined_data.drop(columns=["Buy_Signal", "Sell_Signal"])

    def calculate_stop(row):
        if row["Signal"] == 1:  # Buy
            return (
                row["close"] - 1 * row["atr"]
            )  # Adjust the multiplier as needed
        elif row["Signal"] == -1:  # Sell
            return (
                row["close"] + 1 * row["atr"]
            )  # Adjust the multiplier as needed
        else:  # No signal
            return None

    refined_data["ATR_Stop"] = refined_data.apply(calculate_stop, axis=1)

    return refined_data
