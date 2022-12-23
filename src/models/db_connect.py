from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session, sessionmaker
from src.classes.trade import Trade
from sqlalchemy.engine import Engine
from src.models.model import create_mappers, metadata_obj
from sqlalchemy.schema import CreateSchema, DropSchema


class DbSession:
    engine: Engine
    session: Session

    @classmethod
    def init_engine(cls):
        cls.engine = create_engine(
            "postgresql://kevinmaingi:password@localhost:5432/postgres",
            future=True,
            echo=True,
        )
        cls.session = sessionmaker(cls.engine)

    @staticmethod
    def reset_db(metadata: MetaData) -> None:
        """Reset the database"""
        with DbSession.engine.connect() as conn:
            for schema in metadata._schemas:
                if conn.dialect.has_schema(conn, schema):
                    conn.execute(DropSchema(schema, cascade=True))
                    conn.commit()
            for schema in metadata._schemas:
                if not conn.dialect.has_schema(conn, schema):
                    conn.execute(CreateSchema(schema))
                    conn.commit()

        metadata.bind = DbSession.session
        metadata.drop_all(DbSession.engine)
        metadata.create_all(DbSession.engine)


# order for reseting the database
DbSession.init_engine()
create_mappers()
DbSession.reset_db(metadata=metadata_obj)


with DbSession.session.begin() as session:
    session.add(Trade(231, 123, 1231, 1231))
    session.commit()
