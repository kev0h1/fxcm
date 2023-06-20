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


class PositionEnum(Enum):
    OPEN = "open"
    CLOSED = "closed"


class ForexPairEnum(Enum):
    EURUSD = "EUR/USD"
    USDJPY = "USD/JPY"  # DO NOT TRADE TOO MUCH UNCERTAINTY
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


class CurrencyEnum(Enum):
    USD = "USD"
    GBP = "GBP"
    AUD = "AUD"
    CAD = "CAD"
    EUR = "EUR"
    CHF = "CHF"
    JPY = "JPY"
    NZD = "NZD"


class SentimentEnum(Enum):
    BULLISH = "better"
    BEARISH = "worse"
    FLAT = "FLAT"


class ImpactEnum(Enum):
    low = "low"
    medium = "medium"
    high = "high"


class CalendarEventEnum(Enum):
    CPI_Q = "CPI q/q"
    CPI_M = "CPI m/m"
    CPI_Y = "CPI y/y"
    UNEMPLOYMENT_RATE = "Unemployment Rate"
    PPI_Q = "PPI q/q"
    PPI_M = "PPI m/m"
    PPI_Y = "PPI y/y"
    GDP_Q = "GDP q/q"
    GDP_M = "GDP m/m"
    GDP_Y = "GDP q/q"
    ESMI = "Empire State Manufacturing Index"  # fine
    FLASH_PMI = "Flash Services PMI"  # fine
    ISM = "ISM Manufacturing PMI"
    Test = "Employment Change q/q"
