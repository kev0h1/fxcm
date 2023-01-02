from src.models.trade_model import create_trading_mapper
from sqlalchemy import MetaData
from src.models.fundamental_model import (
    create_fundamental_mapper,
)

SCHEMA_NAME = "fxcm_trading"
metadata_obj = MetaData(schema=SCHEMA_NAME)


def create_mappers():
    """Create mappers for models"""
    create_trading_mapper(metadata_obj=metadata_obj)
    create_fundamental_mapper(metadata_obj=metadata_obj)
