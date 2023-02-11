from sqlalchemy.orm import Session
from src.models.db_connect import context


class BaseRepository:
    def get_session(self) -> Session:
        """Get the session object"""
        return context.get("session")

    def add(self, obj):
        """Add an object"""
        session: Session = self.get_session()
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj
