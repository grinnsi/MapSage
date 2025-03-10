import os
from typing import Optional
from uuid import UUID
import orjson
from sqlmodel import select, text
from flask import Response, request, current_app
from server.database.db import Database, DatabaseSession
from server.database.models import CollectionTable, Connection
from server.ogc_apis.features.implementation import static

from osgeo import gdal, ogr

from server.ogc_apis.features.implementation.dynamic import collection_impl
from server.web.flask_utils import get_app_url_root

# FIXME: Only return a page worth of collections at a time (handle pagination)
def get_all_collections():
    # Not pretty, since we normally use the Database class to interact, but otherwise it would be more complicated
    with DatabaseSession() as session:
        collections: Optional[list[CollectionTable]] = session.exec(select(CollectionTable)).all()
        
        if not collections:
            collections = []
        
        app_url_root = get_app_url_root()
        
        json_data = [{
            "uuid": collection.uuid,
            "id": collection.id,
            "title": collection.title,
            "description": collection.description,
            "license_title": collection.license_title,
            "extent": collection.extent_json,
            "spatial_extent_crs": collection.spatial_extent_crs,
            "temporal_extent_trs": collection.temporal_extent_trs,
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
            new_collection = collection_impl.generate_collection_table_object(form["layer_name"], form["uuid"], dataset, app_url_root)
    else:
        new_collection = collection_impl.generate_collection_table_object(form["layer_name"], form["uuid"], dataset, app_url_root)
    
    new_collection = Database.insert_sqlite_db(new_collection)
    
    if connection_string is None and dataset is None:
        return Response(status=201, response="Collection created")
    else:
        return new_collection

def create_collections(form: dict):
    connection: Connection = Database.select_sqlite_db(table_model=Connection, primary_key_value=form["uuid"])
    connection_string = Database.get_postgresql_connection_string(connection.model_dump())
    
    successful_layers = []
    failed_layers = []
    
    gdal.UseExceptions()
    
    dataset: gdal.Dataset
    with gdal.OpenEx(connection_string) as dataset:
        layer_count = dataset.GetLayerCount()
        for i in range(layer_count):
            layer: ogr.Layer = dataset.GetLayerByIndex(i)
            layer_name = layer.GetName()
            
            data = {
                "layer_name": layer_name,
                "uuid": form["uuid"]
            }
            
            try:
                create_collection(data, connection_string, dataset)
                successful_layers.append(layer_name)
            except Exception as e:
                current_app.logger.error(f"Error creating collection for layer {layer_name}: {e}")
                failed_layers.append(layer_name)
    
    static.collections.update_database_object(app_base_url=get_app_url_root())
    
    if len(successful_layers) == layer_count:
        return Response(status=201, response=orjson.dumps({"message": "All collections created", "successful_layers": successful_layers}))
    elif len(failed_layers) == layer_count:
        return Response(status=500, response=orjson.dumps({"message": "All collections failed", "failed_layers": failed_layers}))
    else:
        return Response(status=207, response=orjson.dumps({"message": "Some collections created", "successful_layers": successful_layers, "failed_layers": failed_layers}))