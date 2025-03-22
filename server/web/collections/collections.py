import os
from typing import Optional
from uuid import UUID
import orjson
from sqlmodel import select, text
from flask import Response, request, current_app
from server.database.db import Database, DatabaseSession
from server.database import models

from osgeo import gdal, ogr

from server.ogc_apis.features.implementation.dynamic import collection_impl
from server.web.flask_utils import get_app_url_root

# FIXME: Only return a page worth of collections at a time (handle pagination)
def get_all_collections():
    # Not pretty, since we normally use the Database class to interact, but otherwise it would be more complicated
    with DatabaseSession() as session:
        collections: Optional[list[models.CollectionTable]] = session.exec(select(models.CollectionTable)).all()
        
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
            # "spatial_extent_crs": collection.spatial_extent_crs,
            # "temporal_extent_trs": collection.temporal_extent_trs,
            "crs": collection.crs_json,
            "storage_crs": collection.storage_crs,
            "storage_crs_coordinate_epoch": collection.storage_crs_coordinate_epoch,
            "connection_name": collection.dataset.name,
            "url": f"{app_url_root}/features/collections/{collection.id}",
        } for collection in collections]      
        
        return json_data

def create_collection(form: dict, connection_string: str = None, gdal_dataset: gdal.Dataset = None):
    if connection_string is None:    
        table_dataset: models.Dataset = Database.select_sqlite_db(table_model=models.Dataset, primary_key_value=form["uuid"])
        connection_string = table_dataset.path
    
    count_existing_collection = Database.select_sqlite_db(text(f" Count(*) FROM {models.CollectionTable.__tablename__} WHERE \"layer_name\" = '{form['layer_name']}' AND \"dataset_uuid\" = '{UUID(form['uuid']).hex}'"))
    if count_existing_collection is not None and count_existing_collection[0] > 0:
        raise ValueError(f"Collection with layer name {form['layer_name']} already exists for this connection.")
    
    app_url_root = get_app_url_root()
    
    if gdal_dataset is None:
        with gdal.OpenEx(connection_string) as gdal_dataset:
            new_collection = collection_impl.generate_collection_table_object(form["layer_name"], form["uuid"], gdal_dataset, app_url_root)
    else:
        new_collection = collection_impl.generate_collection_table_object(form["layer_name"], form["uuid"], gdal_dataset, app_url_root)
    
    new_collection = Database.insert_sqlite_db(new_collection)
    
    if connection_string is None and gdal_dataset is None:
        return Response(status=201, response="Collection created")
    else:
        return new_collection

def create_collections(form: dict):
    table_dataset: models.Dataset = Database.select_sqlite_db(table_model=models.Dataset, primary_key_value=form["uuid"])
    connection_string = table_dataset.path
    
    successful_layers = []
    failed_layers = []
    
    gdal.UseExceptions()
    
    gdal_dataset: gdal.Dataset
    with gdal.OpenEx(connection_string) as gdal_dataset:
        layer_count = gdal_dataset.GetLayerCount()
        for i in range(layer_count):
            layer: ogr.Layer = gdal_dataset.GetLayerByIndex(i)
            layer_name = layer.GetName()
            
            data = {
                "layer_name": layer_name,
                "uuid": form["uuid"]
            }
            
            try:
                create_collection(data, connection_string, gdal_dataset)
                successful_layers.append(layer_name)
            except Exception as e:
                current_app.logger.error(f"Error creating collection for layer {layer_name}: {e}")
                failed_layers.append(layer_name)
    
    if len(successful_layers) == layer_count:
        return Response(status=201, response=orjson.dumps({"message": "All collections created", "successful_layers": successful_layers}))
    elif len(failed_layers) == layer_count:
        return Response(status=500, response=orjson.dumps({"message": "All collections failed", "failed_layers": failed_layers}))
    else:
        return Response(status=207, response=orjson.dumps({"message": "Some collections created", "successful_layers": successful_layers, "failed_layers": failed_layers}))

def delete_collections(form: dict):
    collection_ids = form.get("uuids", None)
    if not collection_ids:
        return Response(status=400, response="Bad request")
    
    collections = Database.delete_sqlite_db(models.CollectionTable, collection_ids)
    if not collections:
        return Response(status=404, response="Collections not found")
    
    return Response(status=204, response="Collections successfully deleted")