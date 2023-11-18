from enum import Enum


class PeriodEnum(str, Enum):
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


class PositionEnum(str, Enum):
    OPEN = "open"
    CLOSED = "closed"


class ForexPairEnum(str, Enum):
    EURUSD = "EUR/USD"
    USDJPY = "USD/JPY"
    GBPUSD = "GBP/USD"
    USDCHF = "USD/CHF"
    USDCAD = "USD/CAD"
    AUDUSD = "AUD/USD"
    NZDUSD = "NZD/USD"
    AUDJPY = "AUD/JPY"
    EURJPY = "EUR/JPY"
    GBPJPY = "GBP/JPY"
    CADCHF = "CAD/CHF"
    CADJPY = "CAD/JPY"
    CHFJPY = "CHF/JPY"
    EURCAD = "EUR/CAD"
    EURCHF = "EUR/CHF"
    EURGBP = "EUR/GBP"
    EURAUD = "EUR/AUD"
    EURNZD = "EUR/NZD"
    GBPCAD = "GBP/CAD"
    GBPCHF = "GBP/CHF"
    GBPAUD = "GBP/AUD"
    GBPNZD = "GBP/NZD"
    AUDCAD = "AUD/CAD"
    AUDCHF = "AUD/CHF"
    AUDNZD = "AUD/NZD"
    NZDCAD = "NZD/CAD"
    NZDCHF = "NZD/CHF"
    NZDJPY = "NZD/JPY"


class GBPConversionMapEnum(str, Enum):
    GBPUSD = "GBP/USD"
    GBPJPY = "GBP/JPY"
    GBPAUD = "GBP/AUD"
    GBPCAD = "GBP/CAD"
    GBPCHF = "GBP/CHF"
    GBPNZD = "GBP/NZD"
    GBPEUR = "EUR/GBP"


conversion_map = {
    ForexPairEnum.EURUSD: GBPConversionMapEnum.GBPUSD,
    ForexPairEnum.USDJPY: GBPConversionMapEnum.GBPJPY,
    ForexPairEnum.GBPUSD: GBPConversionMapEnum.GBPUSD,
    ForexPairEnum.USDCHF: GBPConversionMapEnum.GBPCHF,
    ForexPairEnum.USDCAD: GBPConversionMapEnum.GBPCAD,
    ForexPairEnum.AUDUSD: GBPConversionMapEnum.GBPUSD,
    ForexPairEnum.NZDUSD: GBPConversionMapEnum.GBPUSD,
    ForexPairEnum.AUDJPY: GBPConversionMapEnum.GBPJPY,
    ForexPairEnum.EURJPY: GBPConversionMapEnum.GBPJPY,
    ForexPairEnum.GBPJPY: GBPConversionMapEnum.GBPJPY,
    ForexPairEnum.CADCHF: GBPConversionMapEnum.GBPCHF,
    ForexPairEnum.CADJPY: GBPConversionMapEnum.GBPJPY,
    ForexPairEnum.CHFJPY: GBPConversionMapEnum.GBPJPY,
    ForexPairEnum.EURCAD: GBPConversionMapEnum.GBPCAD,
    ForexPairEnum.EURCHF: GBPConversionMapEnum.GBPCHF,
    ForexPairEnum.EURGBP: GBPConversionMapEnum.GBPEUR,
    ForexPairEnum.EURAUD: GBPConversionMapEnum.GBPAUD,
    ForexPairEnum.EURNZD: GBPConversionMapEnum.GBPNZD,
    ForexPairEnum.GBPCAD: GBPConversionMapEnum.GBPCAD,
    ForexPairEnum.GBPCHF: GBPConversionMapEnum.GBPCHF,
    ForexPairEnum.GBPAUD: GBPConversionMapEnum.GBPAUD,
    ForexPairEnum.GBPNZD: GBPConversionMapEnum.GBPNZD,
    ForexPairEnum.AUDCAD: GBPConversionMapEnum.GBPCAD,
    ForexPairEnum.AUDCHF: GBPConversionMapEnum.GBPCHF,
    ForexPairEnum.AUDNZD: GBPConversionMapEnum.GBPNZD,
    ForexPairEnum.NZDCAD: GBPConversionMapEnum.GBPCAD,
    ForexPairEnum.NZDCHF: GBPConversionMapEnum.GBPCHF,
    ForexPairEnum.NZDJPY: GBPConversionMapEnum.GBPJPY,
}


class OrderTypeEnum(str, Enum):
    AT_MARKET = "AtMarket"
    MARKET_RANGE = "MarketRange"
    MARKET = "MARKET"


class SignalTypeEnum(str, Enum):
    MOVING_AVERAGE = "Moving Average"
    MACD = "MACD"


class CurrencyEnum(str, Enum):
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


class DebugEnum(Enum):
    RunFundamentalEvent = "Run Fundamental Event"
    PublishEvent = "Publish Event"
    RunIndicatorEvent = "Run Indicator Event"
    TestOanda = "Test Oanda"
    TestOpenTrade = "Test Open Trade"
    TestGetTrades = "Test Get Open Trades"
    TestCloseTrade = "Test Close Trade"
    TestManageTrade = "Test Manage Trade"
    LoadData = "Load Data"
    TestModifyTrade = "Test Modify Trade"
    GetTradeState = "Get Trade State"
    TestGetPendingOrders = "Test Get Pending Orders"
    TestCancelPendingOrder = "Test Cancel Pending Order"
    TestProcessEvents = "Test Process Events"
    TestGetSpread = "Test Get Spread"
