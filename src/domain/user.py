from dataclasses import dataclass
from decimal import Decimal


@dataclass
class User:
    id: str
    name: str
    email: str
    password: str
    position_size: Decimal
