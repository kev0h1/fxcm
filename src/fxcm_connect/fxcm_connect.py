import dotenv
from fxcmpy import fxcmpy
import os
from pandas import DataFrame
from src.config import ForexPairEnum, PeriodEnum

env = os.path.abspath(os.curdir) + "\\src\\.env"
config = dotenv.dotenv_values(env)


class FXCMConnect:
    def __init__(self, conf: dict) -> None:
        """set up the connection to fxcm"""
        token = conf["TOKEN"] if "TOKEN" in conf else None

        if token is None:
            raise ValueError("No config defined")
        self.con = fxcmpy(
            access_token=token or conf["TOKEN"], log_level="error"
        )

    def get_candle_data(
        self, instrument: ForexPairEnum, period: PeriodEnum, number: int = 100
    ) -> DataFrame:
        """get the candle data for an instrument"""
        return self.con.get_candles(
            instrument=instrument.value, period=period.value, number=number
        )
