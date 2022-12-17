import os

import pandas as pd

from src.data.data import Data
from src.indicators.indicators import Indicators

file = os.path.abspath(os.curdir) + "/test/data.csv"


class TestIndicators:
    def test_get_simple_moving_average(self):
        """test get simple average"""
        data = pd.read_csv(file)
        data_obj = Data(data)
        refined_data = data_obj.get_refined_data()
        indicators = Indicators()
        data = indicators.get_simple_moving_average(refined_data, 5, "close")
        assert "SMA5" in data
        assert len(data.columns) == 7

    def test_get_exponential_moving_average(self):
        """test get exponential moving average"""
        data = pd.read_csv(file)
        data_obj = Data(data)
        refined_data = data_obj.get_refined_data()
        indicators = Indicators()
        data = indicators.get_exponential_moving_average(
            refined_data, 5, "close"
        )
        assert "EMA5" in data
        assert len(data.columns) == 7

    def test_get_macd(self):
        """Test the get macd method"""
        data = pd.read_csv(file)
        data_obj = Data(data)
        refined_data = data_obj.get_refined_data()
        indicators = Indicators()
        data = indicators.get_macd(refined_data, "close")
        assert "macd" in data
        assert "macd_h" in data
        assert "macd_s" in data
        assert len(data.columns) == 9

    def test_get_stochastic(self):
        """Test the get stocastic method"""
        data = pd.read_csv(file)
        data_obj = Data(data)
        refined_data = data_obj.get_refined_data()
        indicators = Indicators()
        data = indicators.get_stocastic(refined_data)
        assert "%K" in data
        assert "%D" in data
        assert len(data.columns) == 8

    def test_get_rsi(self):
        """Test the get stocastic method"""
        data = pd.read_csv(file)
        data_obj = Data(data)
        refined_data = data_obj.get_refined_data()
        indicators = Indicators()
        data = indicators.get_rsi(refined_data)
        assert "rsi" in data
        assert len(data.columns) == 7

    def test_get_rsi_without_ema(self):
        """Test the get rsi method"""
        data = pd.read_csv(file)
        data_obj = Data(data)
        refined_data = data_obj.get_refined_data()
        indicators = Indicators()
        data = indicators.get_rsi(refined_data, ema=False)
        assert "rsi" in data
        assert len(data.columns) == 7

    def test_get_bollinger(self):
        """Test the get stocastic method"""
        data = pd.read_csv(file)
        data_obj = Data(data)
        refined_data = data_obj.get_refined_data()
        indicators = Indicators()
        data = indicators.get_bollinger(refined_data)
        assert "bollinger_up" in data
        assert "bollinger_down" in data
        assert "SMA20" in data
        assert len(data.columns) == 9

    def test_get_adx(self):
        """Test the get stocastic method"""
        data = pd.read_csv(file)
        data_obj = Data(data)
        refined_data = data_obj.get_refined_data()
        indicators = Indicators()
        data = indicators.get_adx(refined_data)
        assert "plus_di" in data
        assert "minus_di" in data
        assert "adx" in data
        assert len(data.columns) == 9

    def test_get_atr(self):
        """Test the get stocastic method"""
        data = pd.read_csv(file)
        data_obj = Data(data)
        refined_data = data_obj.get_refined_data()
        indicators = Indicators()
        data = indicators.get_atr(refined_data)
        assert "atr" in data
        assert len(data.columns) == 7

    def test_get_obv(self):
        """Test the get stocastic method"""
        data = pd.read_csv(file)
        data_obj = Data(data)
        refined_data = data_obj.get_refined_data()
        indicators = Indicators()
        data = indicators.get_obv(refined_data)
        assert "obv" in data
        assert len(data.columns) == 7

    def test_get_accumulation_distribution(self):
        """Test the get stocastic method"""
        data = pd.read_csv(file)
        data_obj = Data(data)
        refined_data = data_obj.get_refined_data()
        indicators = Indicators()
        data = indicators.get_accumulation_distribution(refined_data)
        assert "ad" in data
        assert len(data.columns) == 7
