from server.database.db import Database
from server.database.models import Connection

from osgeo import gdal

# FIXME: Only return a page woth of collections at a time (handle pagination)
def get_all_collections():
    pass

def create_collection():
    pass

def create_collections(form: dict):
    connection: Connection = Database.select_sqlite_db(table_model=Connection, uuid=form["uuid"])
    connection_string = Database.get_postgresql_connection_string(connection.model_dump(by_alias=True, exclude_unset=True))
    
    with gdal.OpenEx(connection_string) as dataset:
        print(dataset.GetLayerCount())