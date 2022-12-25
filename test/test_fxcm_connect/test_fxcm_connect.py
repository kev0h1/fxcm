import mock
import pandas as pd
import pytest
from fxcmpy import fxcmpy
from hypothesis.strategies import floats, text, booleans, integers
from src.config import ForexPairEnum, PeriodEnum
from src.fxcm_connect.fxcm_connect import FXCMConnect, config

with mock.patch.object(fxcmpy, "__init__", return_value=None):
    fxcm = FXCMConnect(conf=config)


class TestFXCMConnect:
    def test_init(self):
        """Init raises value error"""
        with mock.patch.object(
            fxcmpy, "__init__", return_value=None
        ), mock.patch.object(FXCMConnect, "open_connection") as open:
            FXCMConnect(conf=config)
            open.assert_called_once()

    def test_init_raises_value_error(self):
        """Init raises value error"""
        with mock.patch.object(
            fxcmpy, "__init__", return_value=None
        ), pytest.raises(ValueError):
            FXCMConnect(conf={})

    def test_get_candles(self):
        """test the get candles call"""
        with mock.patch.object(
            fxcmpy, "get_candles", return_value=None
        ) as mock_get:
            fxcm.get_candle_data(
                instrument=ForexPairEnum.USDCAD, period=PeriodEnum.MINUTE_1
            )
            mock_get.assert_called_once_with(
                instrument=ForexPairEnum.USDCAD.value,
                period=PeriodEnum.MINUTE_1.value,
                number=100,
            )

    def test_get_connection_status(self):
        """Test the connection to fxcm"""
        with mock.patch.object(
            fxcmpy, "is_connected", return_value=None
        ) as con:
            fxcm.get_connection_status()
            con.assert_called_once()

    def test_close_connection(self):
        """Close the connection to fxcm"""
        with mock.patch.object(fxcmpy, "close", return_value=None) as con:
            fxcm.close_connection()
            con.assert_called_once()

    def test_open_connection(self):
        """Test the opening of the connection"""
        with mock.patch.object(fxcmpy, "__init__", return_value=None) as con:
            fxcm.open_connection()
            con.assert_called_once_with(
                access_token=fxcm.token, log_level="error"
            )

    def test_get_open_positions(self):
        """Close the connection to fxcm"""
        with mock.patch.object(fxcmpy, "get_open_positions") as con:
            fxcm.get_open_positions()
            con.assert_called_once()

    def test_open_trade(self):
        """Test the opening of a trade"""
        with mock.patch.object(fxcmpy, "open_trade") as con:
            fxcm.open_trade()
