from typing import Callable
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.schema import CreateSchema, DropSchema
from contextlib import contextmanager, AbstractContextManager


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

    @contextmanager
    def session(self) -> Callable[..., AbstractContextManager[Session]]:
        session: Session = self._session_factory()
        try:
            yield session
        except Exception:
            # logger.exception("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()
