from fastapi_restful import set_responses, Resource
from src.models.db_connect import DbSession
from src.models.model import metadata_obj
from src.scheduler.scheduler import get_fundamental_trend_data


class DebugResource(Resource):
    @set_responses(str, 200)
    def delete(self):
        """Deletes the database"""
        DbSession.reset_db(metadata_obj)
        return "done"

    @set_responses(str, 200)
    def put(self):
        """Deletes the database"""
        get_fundamental_trend_data()
        return "done"
