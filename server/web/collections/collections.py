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
    
gdal.UseExceptions()

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
            "connection_name": collection.dataset.name,
            "url": f"{app_url_root}/features/collections/{collection.id}",
        } for collection in collections]
        
        return json_data

def get_collection_details(collection_uuid: str):
    with DatabaseSession() as session:
        collection_uuid = UUID(collection_uuid)
        collection: Optional[models.CollectionTable] = session.get(models.CollectionTable, collection_uuid)
        if not collection:
            return Response(status=404, response="Collection not found")
        
        date_time_fields = []
        with gdal.OpenEx(collection.dataset.path) as gdal_dataset:
            layer: ogr.Layer = gdal_dataset.GetLayerByName(collection.layer_name)
            if layer is not None:
                layer_defn: ogr.FeatureDefn = layer.GetLayerDefn()
                for i in range(layer_defn.GetFieldCount()):
                    field_defn: ogr.FieldDefn = layer_defn.GetFieldDefn(i)
                    if field_defn.GetType() in [ogr.OFTDateTime, ogr.OFTDate, ogr.OFTTime]:
                        date_time_fields.append(field_defn.GetName())
    
    app_url_root = get_app_url_root()
    
    json_data = {
        "uuid": collection.uuid,
        "id": collection.id,
        "title": collection.title,
        "description": collection.description,
        "license_title": collection.license_title,
        "connection_name": collection.dataset.name,
        "url": f"{app_url_root}/features/collections/{collection.id}",
        
        "extent": collection.extent_json,
        # "spatial_extent_crs": collection.spatial_extent_crs,
        # "temporal_extent_trs": collection.temporal_extent_trs,
        "date_time_fields": date_time_fields,
        "selected_date_time_field": collection.date_time_field,
        "crs": collection.crs_json,
        "storage_crs": collection.storage_crs,
        "storage_crs_coordinate_epoch": collection.storage_crs_coordinate_epoch,
    }
    
    return json_data

def create_collection(form: dict, connection_string: str = None, gdal_dataset: gdal.Dataset = None, return_object: bool = True):
    if connection_string is None:    
        table_dataset: models.Dataset = Database.select_sqlite_db(table_model=models.Dataset, primary_key_value=form["uuid"])
        connection_string = table_dataset.path
    
    count_existing_collection = Database.select_sqlite_db(text(f" Count(*) FROM {models.CollectionTable.__tablename__} WHERE \"layer_name\" = '{form['layer_name']}' AND \"dataset_uuid\" = '{UUID(form['uuid']).hex}'"))
    if count_existing_collection is not None and count_existing_collection[0] > 0:
        return Response(status=409, response="Collection already exists")
    
    app_url_root = get_app_url_root()
    
    if gdal_dataset is None:
        with gdal.OpenEx(connection_string) as gdal_dataset:
            new_collection = collection_impl.generate_collection_table_object(form["layer_name"], form["uuid"], gdal_dataset, app_url_root)
    else:
        new_collection = collection_impl.generate_collection_table_object(form["layer_name"], form["uuid"], gdal_dataset, app_url_root)
    
    new_collection = Database.insert_sqlite_db(new_collection)
    
    if return_object:
        return new_collection
    else:
        return Response(status=201, response="Collection created")

def create_collections(form: dict):
    table_dataset: models.Dataset = Database.select_sqlite_db(table_model=models.Dataset, primary_key_value=form["uuid"])
    connection_string = table_dataset.path
    
    successful_layers = []
    failed_layers = []
    
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

def update_collection(uuid: str, form: dict):
    with DatabaseSession() as session:
        collection: models.CollectionTable = session.get(models.CollectionTable, UUID(uuid))
        if not collection:
            return Response(status=404, response="Collection not found")
        
        app_url_root = get_app_url_root()
        if "selected_date_time_field" in form:
            form.setdefault("uuid", collection.uuid)
            form.setdefault("id", collection.id)
            form.setdefault("title", collection.title)
            form.setdefault("description", collection.description)
            form.setdefault("license_title", collection.license_title)
            with gdal.OpenEx(collection.dataset.path) as gdal_dataset:
                collection = collection_impl.generate_collection_table_object(collection.layer_name, collection.dataset.uuid, gdal_dataset, app_url_root, form)
        else:
            for key, value in form.items():
                if key in ["uuid", "id"]:
                    continue
                
                if hasattr(collection, key):
                    setattr(collection, key, value)
            
            collection.pre_render(app_base_url=app_url_root)
        
    Database.update_sqlite_db(collection, collection.uuid)
    
    collection_information = get_collection_details(collection.uuid.__str__())
    return Response(status=200, response=orjson.dumps(collection_information))