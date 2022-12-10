
from src.config import ForexPairEnum, PeriodEnum
from src.fxcm_connect.fxcm_connect import FXCMConnect, config


if __name__ == "__main__":
    hello = FXCMConnect(conf=config)
    data = hello.get_candle_data(ForexPairEnum.USDCAD, PeriodEnum.DAY)
    data = hello.get_refined_data(data)
    print("hiii")