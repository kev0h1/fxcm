import pandas as pd
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.service_layer.indicators import Indicators
pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)


async def divergence_convergence(refined_data: pd.DataFrame, indicator: "Indicators"):
    refined_data = await indicator.get_macd(refined_data, "close")

    refined_data = await indicator.get_rsi(refined_data, period=14)

    refined_data = await indicator.get_atr(refined_data, period=14)

    refined_data = await indicator.get_adx(refined_data, period=14)

    condition_adx_gt_25 = refined_data["adx"] > 25

    atr_threshold = 1.5 * refined_data["atr"].rolling(window=100).mean()

    window_size = 1

    rolling_adx_25 = condition_adx_gt_25.rolling(window_size).sum()

    refined_data["macd"] = (
        refined_data["close"] - refined_data["close"].rolling(window=10).mean()
    )
    refined_data["rsi"] = 100 - 100 / (
        1
        + (
            refined_data["close"]
            .diff()
            .dropna()
            .apply(lambda x: x if x > 0 else 0)
            .rolling(window=14)
            .mean()
            / refined_data["close"]
            .diff()
            .dropna()
            .apply(lambda x: -x if x < 0 else 0)
            .rolling(window=14)
            .mean()
        )
    )

    # Find the most recent peak and trough for each rolling window
    def find_peak_trough(series):
        peak_value = series.iloc[:-1].max()
        trough_value = series.iloc[:-1].min()
        peak_index = series[series == peak_value].index[-1]
        trough_index = series[series == trough_value].index[-1]
        return peak_value, trough_value, peak_index, trough_index

    rolling_window = 14
    refined_data["most_recent_peak"] = np.nan
    refined_data["most_recent_trough"] = np.nan

    for i in range(rolling_window, len(refined_data)):
        window = refined_data["close"].iloc[i - rolling_window : i]
        peak, trough, peak_index, trough_index = find_peak_trough(window)
        refined_data.loc[i, "most_recent_peak"] = peak
        refined_data.loc[i, "most_recent_trough"] = trough
        refined_data.loc[i, "macd_at_peak"] = refined_data["macd"].iloc[peak_index]
        refined_data.loc[i, "macd_at_trough"] = refined_data["macd"].iloc[trough_index]

    # Define divergence conditions
    condition_bullish_divergence = (
        (refined_data["close"] < refined_data["most_recent_trough"])
        & (refined_data["macd"] > refined_data["macd_at_trough"])
        & (refined_data["rsi"] < 30)
        & (rolling_adx_25 > 0)
        & (refined_data["atr"] < atr_threshold)
    )

    condition_bearish_divergence = (
        (refined_data["close"] > refined_data["most_recent_peak"])
        & (refined_data["macd"] < refined_data["macd_at_peak"])
        & (refined_data["rsi"] > 70)
        & (rolling_adx_25 > 0)
        & (refined_data["atr"] < atr_threshold)
    )

    # Create signals
    refined_data["Buy_Signal"] = condition_bullish_divergence
    refined_data["Sell_Signal"] = condition_bearish_divergence

    return refined_data
