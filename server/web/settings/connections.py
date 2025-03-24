from typing import Union
from flask import Response
import orjson

from server.database import models
from server.database.db import Database

from osgeo import gdal, ogr

gdal.UseExceptions()

def get_connections() -> Response:
    """Gets all connections to a (PostgreSQL) database from the internal database and returns a Response with the data and status"""
    
    results: Union[list[models.Dataset], None] = Database.select_sqlite_db(table_model=models.Dataset, select_all=True)

    if not results:
        results = []

    json_data = []
    
    for dataset in results:
        dataset_dict = dataset.to_dict()
        json_data.append(dataset_dict)

    json_data.sort(key=lambda x: x["name"])
    return json_data

def create_new_connection(form: dict) -> Response:
    """Creates a new database connection to a (PostgreSQL) database and stores the parameters in the internal database"""
    
    test_successful = Database.test_pg_connection(form)
    
    if test_successful:
        form["type"] = models.Dataset.Type.DB
        new_connection: models.Dataset = models.Dataset.from_dict(form)       
        new_connection = Database.insert_sqlite_db(data_object=new_connection)
        if new_connection is None:
            return Response(status=500, response="Error while inserting connection into database")

        return Response(status=201, response="Connection successfully created")
    
    return Response(status=400, response="Connection parameters incorrect")

def delete_connection(uuid: str) -> Response:
    """Deletes a connection from the internal database"""
    
    connection: Union[None, models.Dataset] = Database.delete_sqlite_db(table_model=models.Dataset, primary_key_value=uuid)
    if not connection:
        return Response(status=404, response="Connection not found")
    
    return Response(status=204, response="Connection successfully deleted")

def get_dataset_layers_information(dataset_uuid: str) -> Response:
    table_dataset: models.Dataset = Database.select_sqlite_db(table_model=models.Dataset, primary_key_value=dataset_uuid)
    if not table_dataset:
        return Response(status=404, response="Dataset not found")
    connection_string = table_dataset.path

    layers = []
    
    gdal_dataset: gdal.Dataset
    with gdal.OpenEx(connection_string) as gdal_dataset:
        for i in range(gdal_dataset.GetLayerCount()):
            layer: ogr.Layer = gdal_dataset.GetLayerByIndex(i)
            layers.append({
                "name": layer.GetName(),
            })
    
    layers.sort(key=lambda x: x["name"])
    return Response(status=200, response=orjson.dumps({"layers": layers}))