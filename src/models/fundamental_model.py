from sqlalchemy import (
    Table,
    Column,
    DateTime,
    MetaData,
    FLOAT,
    Enum,
    PrimaryKeyConstraint,
    ForeignKeyConstraint,
)
from src.config import CurrencyEnum, CalendarEventEnum, SentimentEnum
from sqlalchemy.orm import registry, relationship
from src.classes.fundamental import FundamentalData


def create_fundamental_data_table(metadata_obj: MetaData):
    """Create the fundamental data table"""
    return Table(
        "fundamental_data",
        metadata_obj,
        Column("currency", Enum(CurrencyEnum)),
        Column("calendar_event", Enum(CalendarEventEnum)),
        Column("sentiment", Enum(SentimentEnum)),
        Column("forecast", FLOAT, nullable=True),
        Column("actual", FLOAT, nullable=True),
        Column("previous", FLOAT, nullable=True),
        Column("last_updated", DateTime),
        PrimaryKeyConstraint("currency", "last_updated", name="pk1"),
    )


def create_fundamental_mapper(metadata_obj: MetaData):
    mapper_registry = registry(metadata=metadata_obj)
    fundamental_data_table = create_fundamental_data_table(
        metadata_obj=metadata_obj
    )

    mapper_registry.map_imperatively(
        FundamentalData,
        fundamental_data_table,
    )
