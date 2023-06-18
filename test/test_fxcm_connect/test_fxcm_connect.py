import mock
import pandas as pd
import pytest
from fxcmpy import fxcmpy
from hypothesis import given
from hypothesis.strategies import (
    floats,
    booleans,
    integers,
    text,
    none,
    from_type,
    builds,
    sampled_from,
)
from src.domain.trade import Trade
from src.config import ForexPairEnum, PeriodEnum, OrderTypeEnum, SignalTypeEnum
from src.domain.errors.errors import InvalidTradeParameter
from src.adapters.fxcm_connect.fxcm_connect import FXCMConnect, config
from mock import MagicMock
import pandas as pd
import os
import pytest

from src.adapters.database.repositories.trade_repository import TradeRepository

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

    @pytest.mark.asyncio
    async def test_init_raises_value_error(self):
        """Init raises value error"""
        with mock.patch.object(
            fxcmpy, "__init__", return_value=None
        ), pytest.raises(ValueError):
            FXCMConnect(conf={})

    @pytest.mark.asyncio
    async def test_get_candles(self):
        """test the get candles call"""
        with mock.patch.object(
            fxcmpy, "get_candles", return_value=None
        ) as mock_get:
            await fxcm.get_candle_data(
                instrument=ForexPairEnum.USDCAD, period=PeriodEnum.MINUTE_1
            )
            mock_get.assert_called_once_with(
                instrument=ForexPairEnum.USDCAD.value,
                period=PeriodEnum.MINUTE_1.value,
                number=100,
            )

    @pytest.mark.asyncio
    async def test_get_connection_status(self):
        """Test the connection to fxcm"""
        with mock.patch.object(
            fxcmpy, "is_connected", return_value=None
        ) as con:
            await fxcm.get_connection_status()
            con.assert_called_once()

    @pytest.mark.asyncio
    async def test_close_connection(self):
        """Close the connection to fxcm"""
        with mock.patch.object(fxcmpy, "close", return_value=None) as con:
            await fxcm.close_connection()
            con.assert_called_once()

    @pytest.mark.asyncio
    async def test_open_connection(self):
        """Test the opening of the connection"""
        with mock.patch.object(fxcmpy, "__init__", return_value=None) as con:
            fxcm.open_connection()
            con.assert_called_once_with(
                access_token=fxcm.token, log_level="error"
            )

    @pytest.mark.asyncio
    async def test_get_open_positions(self):
        """Close the connection to fxcm"""
        with mock.patch.object(fxcmpy, "get_open_positions") as con:
            await fxcm.get_open_positions()
            con.assert_called_once()

    @pytest.mark.asyncio
    @given(
        booleans(),
        booleans(),
        integers(),
        floats(min_value=-1, max_value=1, allow_nan=False),
        floats(min_value=-1, max_value=1, allow_nan=False),
    )
    async def test_open_trade(self, is_buy, is_pips, amount, stop, limit):
        """Test the opening of a trade"""
        session = MagicMock()
        instrument = ForexPairEnum.USDCAD
        is_buy = is_buy
        is_pips = is_pips
        amount = amount
        stop = stop
        limit = limit
        order_type = OrderTypeEnum.AT_MARKET
        time_in_force = "GTC"
        stops = {"limit": limit, "stop": stop}
        with mock.patch.object(fxcmpy, "open_trade") as con, mock.patch.object(
            FXCMConnect, "validate_stops"
        ) as v_stop, mock.patch.object(
            FXCMConnect, "create_trade_obj"
        ) as create:
            await fxcm.open_trade(
                session=session,
                instrument=instrument,
                is_buy=is_buy,
                is_pips=is_pips,
                amount=amount,
                stop=stop,
                limit=limit,
            )
            v_stop.assert_called_once_with(is_buy, is_pips, stop, limit)
            create.assert_called_once_with(session)
            con.assert_called_once_with(
                symbol=instrument.value,
                is_buy=is_buy,
                is_in_pips=is_pips,
                amount=amount,
                time_in_force=time_in_force,
                order_type=order_type.value,
                **stops
            )

    @pytest.mark.asyncio
    @given(booleans(), booleans(), none(), floats())
    async def test_validate_stops_when_stop_none(
        self, is_buy, is_pips, stop, limit
    ):
        """Test the validation of stops on a trade, error raise when stop is none"""
        with pytest.raises(InvalidTradeParameter):
            await fxcm.validate_stops(is_buy, is_pips, stop, limit)

    @pytest.mark.asyncio
    @given(booleans(), booleans(), floats(), floats(max_value=-1))
    async def test_validate_stops_for_invalid_limit(
        self, is_buy, _, stop, limit
    ):
        """Test the validation of stops on a trade, error raise when limit is less than 0"""
        with pytest.raises(InvalidTradeParameter):
            await fxcm.validate_stops(is_buy, True, stop, limit)

    @pytest.mark.asyncio
    @given(booleans(), booleans(), floats(min_value=1), floats())
    async def test_validate_stops_for_invalid_stop(
        self, is_buy, _, stop, limit
    ):
        """Test the validation of stops on a trade, error raise when stop is greater than 0"""
        with pytest.raises(InvalidTradeParameter):
            await fxcm.validate_stops(is_buy, True, stop, limit)

    @pytest.mark.asyncio
    @given(
        floats(min_value=10, max_value=20), floats(min_value=0, max_value=9)
    )
    @pytest.mark.asyncio
    async def test_validate_stops_for_invalid_buy(self, stop, limit):
        """Test the validation of stops on a trade, error raise for invalid buy stops"""
        with pytest.raises(InvalidTradeParameter):
            await fxcm.validate_stops(True, False, stop, limit)

    @pytest.mark.asyncio
    @given(
        floats(min_value=0, max_value=9), floats(min_value=10, max_value=20)
    )
    async def test_validate_stops_for_invalid_sell(self, stop, limit):
        """Test the validation of stops on a trade, error raise for invalid buy stops"""
        with pytest.raises(InvalidTradeParameter):
            await fxcm.validate_stops(False, False, stop, limit)

    @pytest.mark.asyncio
    @given(text(), integers())
    async def test_close_trade(self, trade_id, amount):
        """Test closing a trade"""
        with mock.patch.object(fxcmpy, "close_trade") as con:
            await fxcm.close_trade(trade_id=trade_id, amount=amount)
            con.assert_called_once_with(trade_id=trade_id, amount=amount)

    @pytest.mark.asyncio
    async def test_create_trade_obj(self):
        """Test the creation of a trade object"""
        file = os.path.abspath(os.curdir) + "/test/open_positions.csv"
        df = pd.read_csv(file)
        repo = TradeRepository()
        with mock.patch.object(
            fxcmpy, "get_open_positions", return_value=df
        ) as con, mock.patch.object(
            TradeRepository, "get_trade_by_trade_id", return_value=None
        ) as get_trade, mock.patch.object(
            Trade, "__init__", return_value=None
        ) as create, mock.patch.object(
            TradeRepository, "save", return_value=None
        ) as add:
            await fxcm.create_trade_obj(trade_repository=repo)
            con.assert_called_once()
            get_trade.assert_called_once()
            create.assert_called_once()
            add.assert_called_once()

    @pytest.mark.asyncio
    @given(
        builds(
            Trade,
            trade_id=integers(),
            position_size=integers(),
            stop=floats(),
            limit=floats(),
            is_buy=booleans(),
            signal=sampled_from(SignalTypeEnum),
        )
    )
    async def test_create_trade_obj_for_existing(self, trade):
        """Test the creation of a trade object"""
        file = os.path.abspath(os.curdir) + "/test/open_positions.csv"
        df = pd.read_csv(file)
        repo = TradeRepository()
        with mock.patch.object(
            fxcmpy, "get_open_positions", return_value=df
        ) as con, mock.patch.object(
            TradeRepository, "get_trade_by_trade_id", return_value=trade
        ) as get_trade, mock.patch.object(
            Trade, "__init__", return_value=None
        ) as create, mock.patch.object(
            TradeRepository, "save", return_value=None
        ) as add:
            await fxcm.create_trade_obj(repo)
            con.assert_called_once()
            get_trade.assert_called_once()
            create.assert_not_called()
            add.assert_not_called()
