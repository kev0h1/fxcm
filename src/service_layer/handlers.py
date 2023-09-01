from __future__ import annotations
from src.config import (
    CurrencyEnum,
    PositionEnum,
    SentimentEnum,
    conversion_map,
)
from src.domain import events
from typing import TYPE_CHECKING
from src.domain.fundamental import FundamentalData

from src.domain.trade import Trade
from src.utils import count_decimal_places

if TYPE_CHECKING:
    from src.service_layer.uow import MongoUnitOfWork

from src.logger import get_logger
from datetime import datetime


logger = get_logger(__name__)


async def close_trade_handler(
    event: events.CloseTradeEvent, uow: MongoUnitOfWork
):
    """Handles a close trade event"""
    logger.info(
        "Handling close trade event for currency %s with sentiment %s"
        % (event.currency, event.sentiment)
    )
    trades: list[Trade] = []
    if event.sentiment == SentimentEnum.BULLISH:
        trades = await uow.trade_repository.get_bearish_trades(event.currency)
    elif event.sentiment == SentimentEnum.BEARISH:
        trades = await uow.trade_repository.get_bullish_trades(event.currency)

    for trade in trades:
        await uow.fxcm_connection.close_trade(
            trade_id=trade.trade_id, amount=trade.units
        )
        trade.position = PositionEnum.CLOSED
        await uow.trade_repository.save(trade)


async def get_combined_techincal_and_fundamental_sentiment(
    event: events.OpenTradeEvent, uow: MongoUnitOfWork, currencies: list[str]
) -> SentimentEnum:
    """Calculates the combined technical and fundamental sentiment"""
    base_currency_fundamentals: FundamentalData = (
        await uow.fundamental_data_repository.get_latest_fundamental_data(
            CurrencyEnum(currencies[0])
        )
    )

    quote_currency_fundamentals: FundamentalData = (
        await uow.fundamental_data_repository.get_latest_fundamental_data(
            CurrencyEnum(currencies[1])
        )
    )

    fundamentals = [base_currency_fundamentals, quote_currency_fundamentals]

    latest_object = max(fundamentals, key=lambda x: x.last_updated)

    logger.info(
        "Latest object is %s, base currency fundamentals is %s, quoted currency fundamentals is %s"
        % (
            latest_object,
            base_currency_fundamentals,
            quote_currency_fundamentals,
        )
    )

    if latest_object.processed == False:
        logger.warning(
            "Latest object is not processed %s and last updated time of %s"
            % (latest_object.currency, latest_object.last_updated)
        )
        return SentimentEnum.FLAT

    if event.sentiment == SentimentEnum.BULLISH and (
        (
            base_currency_fundamentals == latest_object
            and base_currency_fundamentals.aggregate_sentiment
            != SentimentEnum.BEARISH
        )
        or (
            quote_currency_fundamentals == latest_object
            and quote_currency_fundamentals.aggregate_sentiment
            != SentimentEnum.BULLISH
        )
    ):
        logger.warning(
            "Combined sentiment is bullish for %s" % event.forex_pair
        )
        return SentimentEnum.BULLISH

    if event.sentiment == SentimentEnum.BEARISH and (
        (
            base_currency_fundamentals == latest_object
            and base_currency_fundamentals.aggregate_sentiment
            != SentimentEnum.BULLISH
        )
        or (
            quote_currency_fundamentals == latest_object
            and quote_currency_fundamentals.aggregate_sentiment
            != SentimentEnum.BEARISH
        )
    ):
        logger.warning(
            "Combined sentiment is bearish for %s" % event.forex_pair
        )
        return SentimentEnum.BEARISH

    logger.warning("Combined sentiment is flat for %s" % event.forex_pair)
    return SentimentEnum.FLAT


async def open_trade_handler(
    event: events.OpenTradeEvent, uow: MongoUnitOfWork
):
    """Handles an open trade event

    (Number of Units) = (Total Equity * Risk per Trade %) / (Stop Loss in Pips * Pip Value)

    Stop Loss in Pips = (Current Price - Stop Loss Price) / Pip Value -> this is 0.0001 for most pairs
    for yen it is 0.01

    (Pip Value) = (0.0001 / Exchange Rate) * Lot Size
    """
    logger.info(
        "Handling open trade event for forex pair %s with sentiment %s"
        % (event.forex_pair, event.sentiment)
    )
    currencies = event.forex_pair.value.split("/")
    is_buy, units, stop_loss, stop_loss_in_pips = await get_trade_parameters(
        event=event, uow=uow, currencies=currencies
    )

    trade_id = None

    trades_open = await uow.trade_repository.get_open_trades_by_forex_pair(
        event.forex_pair
    )

    if len(trades_open) != 0:
        logger.info(
            "There are %s open trades for forex pair %s"
            % (len(trades_open), event.forex_pair)
        )
        return

    if (
        await get_combined_techincal_and_fundamental_sentiment(
            event=event, uow=uow, currencies=currencies
        )
        == SentimentEnum.BULLISH
    ):
        trade_id = await uow.fxcm_connection.open_trade(
            instrument=event.forex_pair,
            is_buy=is_buy,
            amount=units,
            stop=stop_loss,
            limit=None,
        )
    elif (
        await get_combined_techincal_and_fundamental_sentiment(
            event=event, uow=uow, currencies=currencies
        )
        == SentimentEnum.BEARISH
    ):
        trade_id = await uow.fxcm_connection.open_trade(
            instrument=event.forex_pair,
            is_buy=is_buy,
            amount=units,
            stop=stop_loss,
            limit=None,
        )
    if trade_id:
        trade = Trade(
            trade_id=trade_id,
            units=units,
            stop=stop_loss,
            limit=event.limit,
            is_buy=True if event.sentiment == SentimentEnum.BULLISH else False,
            base_currency=CurrencyEnum(currencies[0]),
            quote_currency=CurrencyEnum(currencies[1]),
            forex_currency_pair=event.forex_pair,
            is_winner=False,
            initiated_date=datetime.now(),
            position=PositionEnum.OPEN,
            close=event.close,
            sl_pips=stop_loss_in_pips,
        )

        await uow.trade_repository.save(trade)
        logger.info(
            "Created trade with trade id %s units: %s sentiment: %s for currency pair %s"
            % (trade_id, units, event.sentiment, event.forex_pair)
        )


async def get_trade_parameters(
    event: events.OpenTradeEvent, uow: MongoUnitOfWork, currencies: list[str]
) -> tuple[bool, int, float, float]:
    """Gets the trade parameters for a given event

    units= Risk per unit in GBP/ Amount at risk in GBP
    Risk per unit in GBP = Account Balance × Risk Percentage
    Risk per unit in GBP= Stop loss in pips × Pip value in GBP

    remember that pip value is 0.0001 for most pairs, but 0.01 for yen pairs
    therefore for a standard lot of 100,000 units, the pip value is 10 for non-yen pairs = 0.0001 * 100,000
    and 1000 for yen pairs = 0.01 * 100,000

    100000
        * (float(await uow.fxcm_connection.get_account_balance()) * risk)
        / (
            stop_loss_pips
            * (100000 * (pip_value * 1 / quoted_currency_exchange_rate))
        )

    """
    is_buy = True if event.sentiment == SentimentEnum.BULLISH else False

    pip_value = 0.0001 if "JPY" not in currencies else 0.01
    risk = 2 / 100

    stop_loss_pips = abs(event.close - event.stop) / pip_value

    quoted_currency_exchange_rate = await uow.fxcm_connection.get_latest_close(
        conversion_map[event.forex_pair]
    )

    balance = float(await uow.fxcm_connection.get_account_balance())
    risk_amount = balance * risk
    adjusted_pip_value = 100000 * pip_value * 1 / quoted_currency_exchange_rate
    stop_loss_in_account_currency = stop_loss_pips * adjusted_pip_value
    desired_trade_size = risk_amount / stop_loss_in_account_currency

    units = desired_trade_size * 10000  # trading a mini lot

    stop_loss = round(event.stop, count_decimal_places(pip_value))

    return is_buy, int(units), stop_loss, stop_loss_pips


async def close_forex_pair_handler(
    event: events.CloseForexPairEvent, uow: MongoUnitOfWork
):
    """Close all trades for a given forex pair"""
    is_buy = True if event.sentiment == SentimentEnum.BULLISH else False
    trades = await uow.trade_repository.get_open_trades_by_forex_pair_for_buy_or_sell(
        event.forex_pair, is_buy
    )
    for trade in trades:
        if trade.forex_currency_pair == event.forex_pair:
            await uow.fxcm_connection.close_trade(
                trade_id=trade.trade_id, amount=trade.units
            )
            trade.position = PositionEnum.CLOSED
            await uow.trade_repository.save(trade)


handlers = {
    events.CloseTradeEvent: close_trade_handler,
    events.OpenTradeEvent: open_trade_handler,
    events.CloseForexPairEvent: close_forex_pair_handler,
}
