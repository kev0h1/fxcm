from dataclasses import dataclass
from src.config import CurrencyEnum
from datetime import datetime


@dataclass
class Trend:
    currency: CurrencyEnum
    last_updated: datetime
    sentiment: 
