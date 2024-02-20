import numpy as np
from pandas import DataFrame, concat
from typing import Optional


class Indicators:
    """Class for calculating indicators"""

    async def get_simple_moving_average(
        self,
        data: DataFrame,
        period: int,
        col: str,
        column_name: Optional[str] = None,
    ) -> DataFrame:
        """Calculate the moving average"""

        if column_name:
            name = column_name
        else:
            name = "SMA" + str(period)
        data[name] = data[col].rolling(period).mean()
        return data

    async def get_exponential_moving_average(
        self, data: DataFrame, period: int, col: str
    ) -> DataFrame:
        """Calculate the moving average"""
        data["EMA" + str(period)] = data[col].ewm(period).mean()
        return data

    async def get_macd(
        self,
        data: DataFrame,
        col: str,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9,
    ) -> DataFrame:
        """Calculate the macd"""
        d = data[col].ewm(span=slow, adjust=False, min_periods=26).mean()
        k = data[col].ewm(span=fast, adjust=False, min_periods=12).mean()

        macd = k - d
        macd_s = macd.ewm(span=signal, adjust=False, min_periods=9).mean()
        macd_h = macd - macd_s
        data["macd"] = data.index.map(macd)
        data["macd_h"] = data.index.map(macd_h)
        data["macd_s"] = data.index.map(macd_s)
        return data

    async def get_stocastic(
        self,
        data: DataFrame,
        period: int = 14,
        d_cal_period: int = 3,
        high_col: str = "high",
        low_col: str = "low",
        close_col: str = "close",
    ) -> DataFrame:
        """Calculate the stocastic"""
        high = data[high_col].rolling(period).max()
        low = data[low_col].rolling(period).min()
        data["%K"] = (data[close_col] - low) * 100 / (high - low)
        data["%D"] = data["%K"].rolling(d_cal_period).mean()
        return data

    async def get_rsi(
        self, data: DataFrame, period: int = 14, ema: bool = True
    ) -> DataFrame:
        """Calculate the rsi"""
        close_delta = data["close"].diff()

        # Make two series: one for lower closes and one for higher closes
        up = close_delta.clip(lower=0)
        down = -1 * close_delta.clip(upper=0)

        if ema == True:
            # Use exponential moving average
            ma_up = up.ewm(
                com=period - 1, adjust=True, min_periods=period
            ).mean()
            ma_down = down.ewm(
                com=period - 1, adjust=True, min_periods=period
            ).mean()
        else:
            # Use simple moving average
            ma_up = up.rolling(window=period).mean()
            ma_down = down.rolling(window=period).mean()

        rsi = ma_up / ma_down
        rsi = 100 - (100 / (1 + rsi))
        data["rsi"] = rsi
        return data

    async def get_bollinger(
        self, data: DataFrame, period: int = 20, col: str = "close"
    ) -> DataFrame:
        """get the bollinger bands"""
        sma = await self.get_simple_moving_average(
            data=data, period=period, col=col
        )
        std = data[col].rolling(period).std()
        bollinger_up = sma[col] + std * 2  # Calculate top band
        bollinger_down = sma[col] - std * 2  # Calculate bottom band
        data["bollinger_up"] = bollinger_up
        data["bollinger_down"] = bollinger_down
        return data

    async def get_adx(
        self,
        data: DataFrame,
        period: int = 20,
        close: str = "close",
        high: str = "high",
        low: str = "low",
    ) -> DataFrame:
        """Get the adx"""
        plus_dm = data[high].diff()
        minus_dm = data[low].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm > 0] = 0

        tr1 = data[high] - data[low]
        tr2 = np.abs(data[high] - data[close].shift(1))
        tr3 = np.abs(data[low] - data[close].shift(1))
        # frames = [tr1, tr2, tr3]
        tr = concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(period).mean()

        plus_di = 100 * (plus_dm.ewm(alpha=1 / period).mean() / atr)
        minus_di = np.abs(100 * (minus_dm.ewm(alpha=1 / period).mean() / atr))
        dx = (np.abs(plus_di - minus_di) / np.abs(plus_di + minus_di)) * 100
        adx = ((dx.shift(1) * (period - 1)) + dx) / period
        adx_smooth = adx.ewm(alpha=1 / period).mean()
        data["plus_di"] = plus_di
        data["minus_di"] = minus_di
        data["adx"] = adx_smooth
        return data

    async def get_atr(
        self,
        data: DataFrame,
        period: int = 14,
        close: str = "close",
        high: str = "high",
        low: str = "low",
    ) -> DataFrame:
        """Get the atr"""
        high_low = data[high] - data[low]
        high_close = np.abs(data[high] - data[close].shift())
        low_close = np.abs(data[low] - data[close].shift())
        ranges = concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)

        # Corrected the ATR calculation here
        atr = true_range.rolling(window=period).mean()

        data["atr"] = atr
        return data

    async def get_obv(
        self, data: DataFrame, close: str = "close", volume: str = "volume"
    ) -> DataFrame:
        """Get the obv"""
        obv = (np.sign(data[close].diff()) * data[volume]).fillna(0).cumsum()
        data["obv"] = obv
        return data

    async def get_accumulation_distribution(
        self,
        data: DataFrame,
        high: str = "high",
        low: str = "low",
        close: str = "close",
        volume: str = "volume",
    ) -> DataFrame:
        """Get the ad"""
        # Current money flow volume
        high_low = data[high] - data[low]
        CMFV = np.multiply(
            np.divide(
                np.subtract(
                    np.subtract(data[low], data[close]),
                    np.subtract(data[high], data[close]),
                ),
                high_low,
            ),
            data[volume],
        )
        ad = []
        for t in range(len(CMFV)):
            if t == 0:
                ad.append(CMFV[t])
            else:
                ad.append(ad[-1] + CMFV[t])

        data["ad"] = ad

        return data

    async def calculate_pivot_points(self, df: DataFrame) -> DataFrame:
        """
        Calculate Pivot Points, Supports and Resistances for data
        """
        df["Pivot"] = (df["high"] + df["low"] + df["close"]) / 3
        df["R1"] = df["Pivot"] + 0.618 * (df["Pivot"] - df["low"])
        df["S1"] = df["Pivot"] - 0.618 * (df["high"] - df["Pivot"])
        df["R2"] = df["Pivot"] + (df["high"] - df["low"])
        df["S2"] = df["Pivot"] - (df["high"] - df["low"])
        df["R3"] = df["high"] + 2 * (df["Pivot"] - df["low"])
        df["S3"] = df["low"] - 2 * (df["high"] - df["Pivot"])
        return df

    async def fibonacci_retracements(
        self,
        frame: DataFrame,
        low_column: str = "low",
        high_column: str = "high",
    ) -> DataFrame:
        """
        Calculate Fibonacci retracement levels
        """
        # Find the highest high and lowest low over some period
        recent_low = frame[low_column].min()
        recent_high = frame[high_column].max()

        # Define Fibonacci levels
        diff = recent_high - recent_low
        frame["Fib_23.6"] = recent_high - 0.236 * diff
        frame["Fib_38.2"] = recent_high - 0.382 * diff
        frame["Fib_50.0"] = recent_high - 0.50 * diff
        frame["Fib_61.8"] = recent_high - 0.618 * diff

        return frame
