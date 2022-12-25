from sqlalchemy import (
    Table,
    Column,
    Integer,
    Boolean,
    DateTime,
    MetaData,
    FLOAT,
    Enum,
)

from src.classes.trade import Trade
from sqlalchemy.orm import registry
from src.config import SignalTypeEnum


def create_trade_table(metadata_obj: MetaData):
    """Create the trade table"""
    return Table(
        "trades",
        metadata_obj,
        Column("trade_id", Integer, primary_key=True),
        Column("position_size", Integer),
        Column("stop", FLOAT, nullable=True),
        Column("limit", FLOAT, nullable=True),
        Column("is_winner", Boolean, nullable=True),
        Column("is_Buy", Boolean),
        Column("signal", Enum(SignalTypeEnum)),
        Column("initiated_date", DateTime),
    )


def create_trading_mapper(metadata_obj: MetaData):
    mapper_registry = registry(metadata=metadata_obj)
    trade_table = create_trade_table(metadata_obj=metadata_obj)
    mapper_registry.map_imperatively(Trade, trade_table)
