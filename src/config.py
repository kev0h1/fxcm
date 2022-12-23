from enum import Enum


class PeriodEnum(Enum):
    MINUTE_1 = "m1"
    MINUTE_5 = "m5"
    MINUTE_15 = "m15"
    MINUTE_30 = "m30"
    HOUR_1 = "H1"
    HOUR_2 = "H2"
    HOUR_3 = "H3"
    HOUR_4 = "H4"
    HOUR_6 = "H6"
    HOUR_8 = "H8"
    DAY = "D1"
    WEEK = "W1"
    MONTH = "M1"


class ForexPairEnum(Enum):
    EURUSD = "EUR/USD"
    USDJPY = "USD/JPY"
    GBPUSD = "GBP/USD"
    USDCHF = "USD/CHF"
    USDCAD = "USD/CAD"
    AUDUSD = "AUD/USD"
    NZDUSD = "NZD/USD"


class OrderTypeEnum(Enum):
    AT_MARKET = "AtMarket"
    MARKET_RANGE = "MarketRange"


class SignalTypeEnum(Enum):
    MOVING_AVERAGE = "Moving Average"
    MACD = "MACD"
