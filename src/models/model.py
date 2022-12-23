from src.models.trade_model import create_trading_mapper
from src.classes.trade import Trade
from sqlalchemy import MetaData

SCHEMA_NAME = "fxcm_trading"
metadata_obj = MetaData(schema=SCHEMA_NAME)


def create_mappers():
    """Create mappers for models"""
    create_trading_mapper(metadata_obj=metadata_obj)
