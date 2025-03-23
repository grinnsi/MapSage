from flask import Response
import orjson
from server.database.db import Database
from server.database.models import License

def get_licenses() -> str:
    licenses: list[License] = Database.select_sqlite_db(License, select_all=True)
    licenses = [{
        "title": license.title 
    } for license in licenses]
    licenses_json = orjson.dumps(licenses)
    
    return Response(licenses_json, mimetype='application/json')