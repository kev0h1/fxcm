from src.container.container import Container

from src.service_layer.indicators import Indicators
from src.service_layer.uow import MongoUnitOfWork

from dependency_injector.wiring import inject, Provide
from fastapi import Depends
from src.config import ForexPairEnum, PeriodEnum, SentimentEnum
from src.service_layer.strategies.divergence_convergence import divergence_convergence
from src.domain.events import (
    CloseForexPairEvent,
    OpenTradeEvent,
)
from src.logger import get_logger
import pandas as pd

logger = get_logger(__name__)


@inject
async def get_technical_signal(
    uow: MongoUnitOfWork = Depends(Provide[Container.uow]),
    indicator: Indicators = Depends(Provide[Container.indicator_service]),
) -> None:  # type: ignore
    """Gets the technical signal for the currency"""
    async with uow:
        for forex_pair in ForexPairEnum.__members__.values():
            refined_data: pd.DataFrame = await uow.fxcm_connection.get_candle_data(
                instrument=ForexPairEnum(forex_pair),
                period=PeriodEnum.MINUTE_5,
                number=250,
            )

            # Choose strategy here
            refined_data = await divergence_convergence(refined_data, indicator)

            # Combine the Buy_Signal and Sell_Signal into a single Signal column
            refined_data["Signal"] = refined_data["Buy_Signal"].replace(
                {True: 1, False: 0}
            ) - refined_data["Sell_Signal"].replace({True: 1, False: 0})

            refined_data = refined_data.drop(columns=["Buy_Signal", "Sell_Signal"])

            def calculate_stop(row):
                atr_multiplier = 4
                if row["Signal"] == 1:  # Buy
                    return (
                        row["close"] - atr_multiplier * row["atr"]
                    )  # Adjust the multiplier as needed
                elif row["Signal"] == -1:  # Sell
                    return (
                        row["close"] + atr_multiplier * row["atr"]
                    )  # Adjust the multiplier as needed
                else:  # No signal
                    return None

            def calculate_limit(row):
                atr_multiplier = 8
                # if row["Signal"] == 1:  # Buy
                #     return (
                #         row["close"] + atr_multiplier * row["atr"]
                #     )  # Adjust the multiplier as needed
                # elif row["Signal"] == -1:  # Sell
                #     return (
                #         row["close"] - atr_multiplier * row["atr"]
                #     )  # Adjust the multiplier as needed
                # else:  # No signal
                return None

            refined_data["ATR_Stop"] = refined_data.apply(calculate_stop, axis=1)
            refined_data["ATR_Limit"] = refined_data.apply(calculate_limit, axis=1)

            if refined_data.iloc[-1]["Signal"] > 0:
                logger.warning("Bullish Signal generated for %s" % forex_pair)
                await uow.publish(
                    CloseForexPairEvent(
                        forex_pair=forex_pair, sentiment=SentimentEnum.BEARISH
                    )
                )
                await uow.publish(
                    OpenTradeEvent(
                        forex_pair=forex_pair,
                        sentiment=SentimentEnum.BULLISH,
                        stop=refined_data.iloc[-1]["ATR_Stop"],
                        close=refined_data.iloc[-1]["close"],
                    )
                )
            elif refined_data.iloc[-1]["Signal"] < 0:
                logger.warning("Bearish Signal generated for %s" % forex_pair)
                await uow.publish(
                    CloseForexPairEvent(
                        forex_pair=forex_pair, sentiment=SentimentEnum.BULLISH
                    )
                )
                await uow.publish(
                    OpenTradeEvent(
                        forex_pair=forex_pair,
                        sentiment=SentimentEnum.BEARISH,
                        stop=refined_data.iloc[-1]["ATR_Stop"],
                        close=refined_data.iloc[-1]["close"],
                    )
                )


async def get_signal(refined_data: pd.DataFrame) -> pd.DataFrame:
    return refined_data
