from typing import Any
from fastapi_restful import Resource


class LogResource(Resource):
    async def get(self) -> Any:
        with open("./src/my_logger.log", "r") as log_file:
            return log_file.readlines()

    async def delete(self) -> str:
        with open("./src/my_logger.log", "w") as log_file:
            log_file.write("")
            return {"message": "Log file cleared"}
