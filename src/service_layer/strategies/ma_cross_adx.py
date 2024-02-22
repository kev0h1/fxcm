import pandas as pd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.service_layer.indicators import Indicators
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)


async def ma_cross_adx(refined_data: pd.DataFrame, indicator: "Indicators"):
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

    refined_data["Prev_ShortTerm_MA"] = refined_data["ShortTerm_MA"].shift(1)
    refined_data["Prev_MediumTerm_MA"] = refined_data["MediumTerm_MA"].shift(1)

    refined_data = await indicator.get_macd(refined_data, "close")

    refined_data = await indicator.get_atr(refined_data, period=14)

    refined_data = await indicator.get_adx(refined_data, period=14)

    refined_data = await indicator.get_obv(refined_data)

    # Define RSI thresholds
    rsi_overbought = 70
    rsi_oversold = 30

    # Define divergence conditions
    condition_bullish_divergence = (
        (refined_data["Prev_ShortTerm_MA"] <= refined_data["Prev_MediumTerm_MA"])
        & (refined_data["ShortTerm_MA"] > refined_data["MediumTerm_MA"])
        & (refined_data["close"] > refined_data["LongTerm_MA"])
        & (refined_data["adx"] > 25)
        & (refined_data["plus_di"] > refined_data["minus_di"])
        & (refined_data["rsi"] > 50)
        & (refined_data["rsi"] < rsi_overbought)
        & (refined_data["obv"].diff().rolling(window=3).mean() > 0)
    )

    condition_bearish_divergence = (
        (refined_data["Prev_ShortTerm_MA"] >= refined_data["Prev_MediumTerm_MA"])
        & (refined_data["ShortTerm_MA"] < refined_data["MediumTerm_MA"])
        & (refined_data["close"] < refined_data["LongTerm_MA"])
        & (refined_data["adx"] > 25)
        & (refined_data["plus_di"] < refined_data["minus_di"])
        & (refined_data["rsi"] < 50)
        & (refined_data["rsi"] > rsi_oversold)
        & (refined_data["obv"].diff().rolling(window=3).mean() < 0)
    )

    # Create signals
    refined_data["Buy_Signal"] = condition_bullish_divergence
    refined_data["Sell_Signal"] = condition_bearish_divergence

    return refined_data
