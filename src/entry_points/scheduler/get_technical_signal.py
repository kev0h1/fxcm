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
import numpy as np

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
                period=5,
                col="close",
                column_name="ShortTerm_MA",
            )
            refined_data = await indicator.get_simple_moving_average(
                refined_data,
                period=10,
                col="close",
                column_name="MediumTerm_MA",
            )
            refined_data = await indicator.get_simple_moving_average(
                refined_data,
                period=50,
                col="close",
                column_name="LongTerm_MA",
            )

            refined_data = await indicator.get_rsi(refined_data, period=14)

            refined_data["Prev_ShortTerm_MA"] = refined_data[
                "ShortTerm_MA"
            ].shift(1)
            refined_data["Prev_MediumTerm_MA"] = refined_data[
                "MediumTerm_MA"
            ].shift(1)

            refined_data = await indicator.get_macd(refined_data, "close")

            refined_data = await indicator.get_atr(refined_data, period=14)

            refined_data = await indicator.get_adx(refined_data, period=14)

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
                        limit=refined_data.iloc[-1]["ATR_Limit"],
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
                        limit=refined_data.iloc[-1]["ATR_Limit"],
                    )
                )


async def get_signal(refined_data: pd.DataFrame) -> pd.DataFrame:
    """Gets the signal for the currency"""

    # Define divergence conditions
    condition_bullish_divergence = (
        (
            refined_data["Prev_ShortTerm_MA"]
            <= refined_data["Prev_MediumTerm_MA"]
        )
        & (refined_data["ShortTerm_MA"] > refined_data["MediumTerm_MA"])
        & (refined_data["close"] > refined_data["LongTerm_MA"])
        & (refined_data["adx"] > 25)
        & (refined_data["plus_di"] > refined_data["minus_di"])
    )

    condition_bearish_divergence = (
        (
            refined_data["Prev_ShortTerm_MA"]
            >= refined_data["Prev_MediumTerm_MA"]
        )
        & (refined_data["ShortTerm_MA"] < refined_data["MediumTerm_MA"])
        & (refined_data["close"] > refined_data["LongTerm_MA"])
        & (refined_data["adx"] > 25)
        & (refined_data["plus_di"] < refined_data["minus_di"])
    )

    # Create signals
    refined_data["Buy_Signal"] = condition_bullish_divergence
    refined_data["Sell_Signal"] = condition_bearish_divergence

    # Combine the Buy_Signal and Sell_Signal into a single Signal column
    refined_data["Signal"] = refined_data["Buy_Signal"].replace(
        {True: 1, False: 0}
    ) - refined_data["Sell_Signal"].replace({True: 1, False: 0})

    refined_data = refined_data.drop(columns=["Buy_Signal", "Sell_Signal"])

    def calculate_stop(row):
        if row["Signal"] == 1:  # Buy
            return (
                row["close"] - 3 * row["atr"]
            )  # Adjust the multiplier as needed
        elif row["Signal"] == -1:  # Sell
            return (
                row["close"] + 3 * row["atr"]
            )  # Adjust the multiplier as needed
        else:  # No signal
            return None

    def calculate_limit(row):
        if row["Signal"] == 1:  # Buy
            return (
                row["close"] + 4 * row["atr"]
            )  # Adjust the multiplier as needed
        elif row["Signal"] == -1:  # Sell
            return (
                row["close"] - 4 * row["atr"]
            )  # Adjust the multiplier as needed
        else:  # No signal
            return None

    refined_data["ATR_Stop"] = refined_data.apply(calculate_stop, axis=1)
    refined_data["ATR_Limit"] = refined_data.apply(calculate_limit, axis=1)

    return refined_data
