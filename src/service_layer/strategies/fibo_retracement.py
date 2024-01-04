import pandas as pd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.service_layer.indicators import Indicators
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)


async def fibo_retracement(refined_data: pd.DataFrame, indicator: "Indicators"):
    refined_data = await indicator.get_simple_moving_average(
        refined_data,
        period=5,
        col="close",
        column_name="MA",
    )
    refined_data = await indicator.fibonacci_retracements(refined_data)

    refined_data = await indicator.get_rsi(refined_data, period=14)

    refined_data = await indicator.get_macd(refined_data, "close")

    refined_data = await indicator.get_atr(refined_data, period=14)

    refined_data = await indicator.get_adx(refined_data, period=14)

    refined_data["prev_close"] = refined_data["close"].shift(1)
    bullish_condition = (
        (
            (
                (refined_data["prev_close"] <= refined_data["Fib_23.6"])
                & (refined_data["close"] > refined_data["Fib_23.6"])
            )
            | (
                (refined_data["prev_close"] <= refined_data["Fib_38.2"])
                & (refined_data["close"] > refined_data["Fib_38.2"])
            )
            | (
                (refined_data["prev_close"] <= refined_data["Fib_50.0"])
                & (refined_data["close"] > refined_data["Fib_50.0"])
            )
            | (
                (refined_data["prev_close"] <= refined_data["Fib_61.8"])
                & (refined_data["close"] > refined_data["Fib_61.8"])
            )
        )
        & (refined_data["close"] > refined_data["Fib_23.6"])
        & (refined_data["close"] > refined_data["MA"])
        & (refined_data["adx"] > 25)
        & (refined_data["plus_di"] > refined_data["minus_di"])
    )

    bearish_condition = (
        (
            (
                (refined_data["prev_close"] >= refined_data["Fib_23.6"])
                & (refined_data["close"] < refined_data["Fib_23.6"])
            )
            | (
                (refined_data["prev_close"] >= refined_data["Fib_38.2"])
                & (refined_data["close"] < refined_data["Fib_38.2"])
            )
            | (
                (refined_data["prev_close"] >= refined_data["Fib_50.0"])
                & (refined_data["close"] < refined_data["Fib_50.0"])
            )
            | (
                (refined_data["prev_close"] >= refined_data["Fib_61.8"])
                & (refined_data["close"] < refined_data["Fib_61.8"])
            )
        )
        & (refined_data["close"] < refined_data["MA"])
        & (refined_data["adx"] > 25)
        & (refined_data["plus_di"] < refined_data["minus_di"])
    )

    # Create signals
    refined_data["Buy_Signal"] = bearish_condition
    refined_data["Sell_Signal"] = bullish_condition

    return refined_data
