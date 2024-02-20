import pandas as pd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.service_layer.indicators import Indicators
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)


async def ma_crossover(refined_data: pd.DataFrame, indicator: "Indicators"):
    refined_data = await indicator.get_simple_moving_average(
        refined_data,
        period=5,
        col="close",
        column_name="ShortTerm_MA",
    )
    refined_data = await indicator.get_simple_moving_average(
        refined_data,
        period=20,
        col="close",
        column_name="MediumTerm_MA",
    )
    refined_data = await indicator.get_simple_moving_average(
        refined_data,
        period=100,
        col="close",
        column_name="LongTerm_MA",
    )

    refined_data = await indicator.get_rsi(refined_data, period=14)

    refined_data = await indicator.get_macd(refined_data, "close")

    refined_data = await indicator.get_atr(refined_data, period=14)

    refined_data = await indicator.get_adx(refined_data, period=14)

    refined_data["Prev_ShortTerm_MA"] = refined_data["ShortTerm_MA"].shift(1)
    refined_data["Prev_MediumTerm_MA"] = refined_data["MediumTerm_MA"].shift(1)

    refined_data["Buy_Signal"] = (
        (refined_data["Prev_ShortTerm_MA"] <= refined_data["Prev_MediumTerm_MA"])
        & (refined_data["ShortTerm_MA"] > refined_data["MediumTerm_MA"])
        & (refined_data["MediumTerm_MA"] > refined_data["LongTerm_MA"])
        & (refined_data["rsi"] > 50)
    )

    # Create a Sell_Signal column that checks if the short term MA has just crossed below the other two MAs and RSI has just crossed below 50
    refined_data["Sell_Signal"] = (
        (refined_data["Prev_ShortTerm_MA"] >= refined_data["Prev_MediumTerm_MA"])
        & (refined_data["ShortTerm_MA"] < refined_data["MediumTerm_MA"])
        & (refined_data["MediumTerm_MA"] < refined_data["LongTerm_MA"])
        & (refined_data["rsi"] < 50)
    )

    return refined_data
