from typing import Union
from fastapi.encoders import jsonable_encoder
from flask import Response
from server.database.db import Database
from server.database.models import GeneralOption


def get_general_options() -> dict:
    """Gets the general options from the internal database and returns them as a dictionary/json"""
    
    options: Union[list[GeneralOption], None] = Database.select_sqlite_db(table_model=GeneralOption, select_all=True)

    if not options:
        options = []

    return jsonable_encoder(options)

def update_general_options(data: list[GeneralOption]) -> Response:
    """Updates the general options in the internal database"""
    
    if len(data) < 1:
        return Response(status=400, response="No data provided")
    
    update_models = [GeneralOption(**d) for d in data]
    
    result = Database.update_sqlite_db(update=update_models)
    
    if not result:
        return Response(status=500, response="Error while updating general options")
    
    return Response(status=201, response="General options updated")