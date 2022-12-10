from src.fxcm_connect.fxcm_connect import FXCMConnect, config
from fxcmpy import fxcmpy
import pandas as pd
import mock
from src.config import ForexPairEnum, PeriodEnum
import pytest


class TestFXCMConnect:
    def test_init(self):
        """Init raises value error"""
        with mock.patch.object(fxcmpy, "__init__", return_value=None):
            FXCMConnect(conf=config)
            assert True

    def test_init_raises_value_error(self):
        """Init raises value error"""
        with mock.patch.object(
            fxcmpy, "__init__", return_value=None
        ), pytest.raises(ValueError):
            FXCMConnect(conf={})

    def test_get_candles(self):
        """test the get candles call"""
        with mock.patch.object(
            fxcmpy, "__init__", return_value=None
        ), mock.patch.object(
            fxcmpy, "get_candles", return_value=None
        ) as mock_get:
            fxcm_connect = FXCMConnect(conf=config)
            fxcm_connect.get_candle_data(
                instrument=ForexPairEnum.USDCAD, period=PeriodEnum.MINUTE_1
            )
            mock_get.assert_called_once_with(
                instrument=ForexPairEnum.USDCAD.value,
                period=PeriodEnum.MINUTE_1.value,
                number=100,
            )
