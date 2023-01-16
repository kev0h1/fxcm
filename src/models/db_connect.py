from typing import Callable
from sqlalchemy import create_engine, MetaData, orm
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema, DropSchema
from contextlib import contextmanager, AbstractContextManager


class Database:
    def __init__(self):
        self._engine = create_engine(
            "postgresql://kevinmaingi:password@localhost:5432/postgres",
            future=True,
            echo=True,
        )
        self._session_factory = orm.scoped_session(
            orm.sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self._engine,
            ),
        )

    def reset_db(self, metadata: MetaData) -> None:
        """Reset the database"""
        with self._engine.connect() as conn:
            for schema in metadata._schemas:
                if conn.dialect.has_schema(conn, schema):
                    conn.execute(DropSchema(schema, cascade=True))
                    conn.commit()
            for schema in metadata._schemas:
                if not conn.dialect.has_schema(conn, schema):
                    conn.execute(CreateSchema(schema))
                    conn.commit()

        # metadata.bind = DbSession.session
        metadata.drop_all(self._engine)
        metadata.create_all(self._engine)

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
