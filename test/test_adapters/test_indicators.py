import os

import pandas as pd
from src.adapters.fxcm_connect.mock_trade_connect import MockTradeConnect
from src.service_layer.indicators import Indicators
import pytest

file = os.path.abspath(os.curdir) + "/test/data.csv"

connect = MockTradeConnect()


class TestIndicators:
    @pytest.mark.asyncio
    async def test_get_simple_moving_average(self):
        """test get simple average"""
        data = pd.read_csv(file)
        refined_data = await connect.get_candle_data()
        indicators = Indicators()
        data = await indicators.get_simple_moving_average(
            refined_data, 5, "close"
        )
        assert "SMA5" in data
        assert len(data.columns) == 7

    @pytest.mark.asyncio
    async def test_get_exponential_moving_average(self):
        """test get exponential moving average"""
        data = pd.read_csv(file)
        refined_data = await connect.get_candle_data()
        indicators = Indicators()
        data = await indicators.get_exponential_moving_average(
            refined_data, 5, "close"
        )
        assert "EMA5" in data
        assert len(data.columns) == 7

    @pytest.mark.asyncio
    async def test_get_macd(self):
        """Test the get macd method"""
        data = pd.read_csv(file)
        refined_data = await connect.get_candle_data()
        indicators = Indicators()
        data = await indicators.get_macd(refined_data, "close")
        assert "macd" in data
        assert "macd_h" in data
        assert "macd_s" in data
        assert len(data.columns) == 9

    @pytest.mark.asyncio
    async def test_get_stochastic(self):
        """Test the get stocastic method"""
        data = pd.read_csv(file)
        refined_data = await connect.get_candle_data()
        indicators = Indicators()
        data = await indicators.get_stocastic(refined_data)
        assert "%K" in data
        assert "%D" in data
        assert len(data.columns) == 8

    @pytest.mark.asyncio
    async def test_get_rsi(self):
        """Test the get stocastic method"""
        data = pd.read_csv(file)
        refined_data = await connect.get_candle_data()
        indicators = Indicators()
        data = await indicators.get_rsi(refined_data)
        assert "rsi" in data
        assert len(data.columns) == 7

    @pytest.mark.asyncio
    async def test_get_rsi_without_ema(self):
        """Test the get rsi method"""
        data = pd.read_csv(file)
        refined_data = await connect.get_candle_data()
        indicators = Indicators()
        data = await indicators.get_rsi(refined_data, ema=False)
        assert "rsi" in data
        assert len(data.columns) == 7

    @pytest.mark.asyncio
    async def test_get_bollinger(self):
        """Test the get stocastic method"""
        data = pd.read_csv(file)
        refined_data = await connect.get_candle_data()
        indicators = Indicators()
        data = await indicators.get_bollinger(refined_data)
        assert "bollinger_up" in data
        assert "bollinger_down" in data
        assert "SMA20" in data
        assert len(data.columns) == 9

    @pytest.mark.asyncio
    async def test_get_adx(self):
        """Test the get stocastic method"""
        data = pd.read_csv(file)
        refined_data = await connect.get_candle_data()
        indicators = Indicators()
        data = await indicators.get_adx(refined_data)
        assert "plus_di" in data
        assert "minus_di" in data
        assert "adx" in data
        assert len(data.columns) == 9

    @pytest.mark.asyncio
    async def test_get_atr(self):
        """Test the get stocastic method"""
        data = pd.read_csv(file)
        refined_data = await connect.get_candle_data()
        indicators = Indicators()
        data = await indicators.get_atr(refined_data)
        assert "atr" in data
        assert len(data.columns) == 7

    @pytest.mark.asyncio
    async def test_get_obv(self):
        """Test the get stocastic method"""
        data = pd.read_csv(file)
        refined_data = await connect.get_candle_data()
        indicators = Indicators()
        data = await indicators.get_obv(refined_data)
        assert "obv" in data
        assert len(data.columns) == 7

    @pytest.mark.asyncio
    async def test_get_accumulation_distribution(self):
        """Test the get stocastic method"""
        data = pd.read_csv(file)
        refined_data = await connect.get_candle_data()
        indicators = Indicators()
        data = await indicators.get_accumulation_distribution(refined_data)
        assert "ad" in data
        assert len(data.columns) == 7
