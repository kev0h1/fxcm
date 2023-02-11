from sqlalchemy import create_engine, MetaData, orm
from sqlalchemy.orm import Session
from sqlalchemy.schema import CreateSchema, DropSchema
from contextvars import ContextVar
from contextlib import contextmanager

context = ContextVar("session")


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
    def get_session(self):
        session: Session = self._session_factory()
        context.set(session)
        try:
            print("opening")
            yield session
        except Exception:
            # logger.exception("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            print("closing")
            session.close()
            context.set("")
