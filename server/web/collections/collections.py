import os
from typing import Optional
from uuid import UUID
from sqlmodel import select, text
from flask import Response, request, current_app
from server.database.db import Database
from server.database.models import CollectionTable, Connection

from osgeo import gdal, ogr

from server.ogc_apis.features.implementation.collection_impl import generate_collection_table_object
from server.web.flask_utils import get_app_url_root

# FIXME: Only return a page worth of collections at a time (handle pagination)
def get_all_collections():
    # Not pretty, since we normally use the Database class to interact, but otherwise it would be more complicated
    with Database.get_sqlite_session() as session:
        collections: Optional[list[CollectionTable]] = session.exec(select(CollectionTable)).all()
        
        if not collections:
            collections = []
        
        app_url_root = request.url_root.removesuffix(os.getenv("DASHBOARD_URL", "dashboard") + "/")
        
        json_data = [{
            "uuid": collection.uuid,
            "id": collection.id,
            "title": collection.title,
            "description": collection.description,
            "license_title": collection.license_title,
            "bbox": collection.bbox_json,
            "bbox_crs": collection.bbox_crs,
            "interval": collection.interval_json,
            "crs": collection.crs_json,
            "storage_crs": collection.storage_crs,
            "storage_crs_coordinate_epoch": collection.storage_crs_coordinate_epoch,
            "connection_name": collection.connection.name,
            "url": f"{app_url_root}features/collections/{collection.id}",
        } for collection in collections]      
        
        return json_data

def create_collection(form: dict, connection_string: str = None, dataset: gdal.Dataset = None):
    if connection_string is None:    
        connection: Connection = Database.select_sqlite_db(table_model=Connection, primary_key_value=form["uuid"])
        connection_string = Database.get_postgresql_connection_string(connection.model_dump())
    
    count_existing_collection = Database.select_sqlite_db(text(f" Count(*) FROM {CollectionTable.__tablename__} WHERE \"layer_name\" = '{form['layer_name']}' AND \"connection_uuid\" = '{UUID(form['uuid']).hex}'"))
    if count_existing_collection is not None and count_existing_collection[0] > 0:
        raise ValueError(f"Collection with layer name {form['layer_name']} already exists for this connection.")
    
    app_url_root = get_app_url_root()
    
    if dataset is None:
        with gdal.OpenEx(connection_string) as dataset:
            new_collection = generate_collection_table_object(form["layer_name"], form["uuid"], dataset, app_url_root)
    else:
        new_collection = generate_collection_table_object(form["layer_name"], form["uuid"], dataset, app_url_root)
    
    new_collection = Database.insert_sqlite_db(new_collection)
    
    if connection_string is None and dataset is None:
        return Response(status=201, response="Collection created")
    else:
        return new_collection

def create_collections(form: dict):
    connection: Connection = Database.select_sqlite_db(table_model=Connection, primary_key_value=form["uuid"])
    connection_string = Database.get_postgresql_connection_string(connection.model_dump())
    
    # TODO: Send succesful and failed collections back to the user to show which collections were created and which failed
    successful = []
    
    gdal.UseExceptions()
    
    dataset: gdal.Dataset
    with gdal.OpenEx(connection_string) as dataset:
        for i in range (dataset.GetLayerCount()):
            layer: ogr.Layer = dataset.GetLayerByIndex(i)
            layer_name = layer.GetName()
            
            data = {
                "layer_name": layer_name,
                "uuid": form["uuid"]
            }
            
            try:
                create_collection(data, connection_string, dataset)
                successful.append(True)
            except Exception as e:
                current_app.logger.error(f"Error creating collection for layer {layer_name}: {e}")
                successful.append(False)
    
    if all(successful):
        return Response(status=201, response="Collections created")
    elif all(successful) is False:
        return Response(status=500, response="Error creating collections")
    else:
        return Response(status=207, response="Some collections created")