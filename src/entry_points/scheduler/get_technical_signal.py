from src.container.container import Container

from src.service_layer.indicators import Indicators
from src.service_layer.uow import MongoUnitOfWork

from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.config import ForexPairEnum, PeriodEnum, SentimentEnum

from src.domain.events import (
    CloseForexPairEvent,
    OpenTradeEvent,
)
from src.logger import get_logger
import pandas as pd

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
logger = get_logger(__name__)


@inject
async def get_technical_signal(
    uow: MongoUnitOfWork = Depends(Provide[Container.uow]),
    indicator: Indicators = Depends(Provide[Container.indicator_service]),
) -> None:  # type: ignore
    """Gets the technical signal for the currency"""
    async with uow:
        for forex_pair in ForexPairEnum.__members__.values():
            refined_data: pd.DataFrame = (
                await uow.fxcm_connection.get_candle_data(
                    instrument=ForexPairEnum(forex_pair),
                    period=PeriodEnum.MINUTE_5,
                    number=250,
                )
            )

            refined_data = await indicator.get_simple_moving_average(
                refined_data,
                period=10,
                col="close",
                column_name="ShortTerm_MA",
            )
            refined_data = await indicator.get_simple_moving_average(
                refined_data,
                period=50,
                col="close",
                column_name="MediumTerm_MA",
            )
            refined_data = await indicator.get_simple_moving_average(
                refined_data,
                period=100,
                col="close",
                column_name="LongTerm_MA",
            )

            refined_data = await indicator.get_rsi(refined_data, period=14)

            refined_data["Prev_ShortTerm_MA"] = refined_data[
                "ShortTerm_MA"
            ].shift(1)
            refined_data["Prev_MediumTerm_MA"] = refined_data[
                "MediumTerm_MA"
            ].shift(1)

            refined_data = await get_signal(refined_data)
            if refined_data.iloc[-1]["Signal"] > 0:
                await uow.publish(
                    CloseForexPairEvent(
                        forex_pair=forex_pair, sentiment=SentimentEnum.BEARISH
                    )
                )
                await uow.publish(
                    OpenTradeEvent(
                        forex_pair=forex_pair,
                        sentiment=SentimentEnum.BULLISH,
                        stop=refined_data.iloc[-1]["LongTerm_MA"],
                        close=refined_data.iloc[-1]["close"],
                    )
                )
            elif refined_data.iloc[-1]["Signal"] < 0:
                await uow.publish(
                    CloseForexPairEvent(
                        forex_pair=forex_pair, sentiment=SentimentEnum.BULLISH
                    )
                )
                await uow.publish(
                    OpenTradeEvent(
                        forex_pair=forex_pair,
                        sentiment=SentimentEnum.BEARISH,
                        stop=refined_data.iloc[-1]["LongTerm_MA"],
                        close=refined_data.iloc[-1]["close"],
                    )
                )


async def get_signal(refined_data: pd.DataFrame) -> pd.DataFrame:
    refined_data["Buy_Signal"] = (
        (
            refined_data["Prev_ShortTerm_MA"]
            <= refined_data["Prev_MediumTerm_MA"]
        )
        & (refined_data["ShortTerm_MA"] > refined_data["MediumTerm_MA"])
        & (refined_data["MediumTerm_MA"] > refined_data["LongTerm_MA"])
        & (refined_data["rsi"] < 30)
    )

    # Create a Sell_Signal column that checks if the short term MA has just crossed below the other two MAs and RSI has just crossed below 50
    refined_data["Sell_Signal"] = (
        (
            refined_data["Prev_ShortTerm_MA"]
            >= refined_data["Prev_MediumTerm_MA"]
        )
        & (refined_data["ShortTerm_MA"] < refined_data["MediumTerm_MA"])
        & (refined_data["MediumTerm_MA"] < refined_data["LongTerm_MA"])
        & (refined_data["rsi"] > 70)
    )

    # Combine the Buy_Signal and Sell_Signal into a single Signal column
    refined_data["Signal"] = refined_data["Buy_Signal"].replace(
        {True: 1, False: 0}
    ) - refined_data["Sell_Signal"].replace({True: 1, False: 0})

    refined_data = refined_data.drop(columns=["Buy_Signal", "Sell_Signal"])

    return refined_data
