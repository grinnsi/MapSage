import os
from typing import Optional
from uuid import UUID
import orjson, math
from sqlmodel import select, text
from flask import Response, request, current_app
from server.database.db import Database
from server.database.models import CollectionTable, Connection

from osgeo import gdal, ogr, osr

from server.ogc_apis.features.implementation.static_content.pre_render import generate_link
from server.utils.crs_identifier import get_uri_of_spatial_ref
from server.utils.string_utils import string_to_kebab

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

        print(json_data)
        
        
        return json_data

def generate_collection_table_object(layer_name: str, connection_uuid: str, dataset: gdal.Dataset) -> CollectionTable:
    gdal.UseExceptions()
    
    new_collection = CollectionTable()
    
    layer: ogr.Layer = dataset.GetLayerByName(layer_name)
    if layer is None:
        raise ValueError(f"Layer {layer_name} not found in dataset {dataset.GetDescription()}")
    
    spatial_ref: osr.SpatialReference = layer.GetSpatialRef()
    if spatial_ref is None:
        raise ValueError(f"Layer {layer_name} has no spatial reference")
    
    # Always calculate the bbx as 3D, just in case it is a 3D layer
    extent_calc: tuple[float] = layer.GetExtent3D()
    
    # Reorder the extent to be in the order of OGC API Features
    # FIXME: Order of axis are east, north; might need to be changed if the layer is in a different order
    extent_ordered = [extent_calc[0], extent_calc[2], extent_calc[1], extent_calc[3]]
    
    # Remove all None/Null values from list, mainly to remove the Z values in 2D layers
    if extent_calc[4] != math.inf or extent_calc[5] != -math.inf:
        extent_ordered.append([extent_calc[4], extent_calc[5]])
    
    new_collection.bbox_json = orjson.dumps(extent_ordered).decode("utf-8")
    
    uri_of_spatial_ref = get_uri_of_spatial_ref(spatial_ref)
    new_collection.bbox_crs = uri_of_spatial_ref
    new_collection.crs_json = orjson.dumps(["http://www.opengis.net/def/crs/OGC/1.3/CRS84", uri_of_spatial_ref]).decode("utf-8")
    new_collection.storage_crs = uri_of_spatial_ref
    
    if spatial_ref.IsDynamic():
        new_collection.storage_crs_coordinate_epoch = spatial_ref.GetCoordinateEpoch()
    
    base_id = string_to_kebab(layer_name.split(".", 1)[-1])
    
    # FIXME: This is a very bad way to generate unique ids
    for i in range(0, 100):
        id = base_id if i == 0 else f"{base_id}-{i}"
        result = Database.select_sqlite_db(text(f" id FROM {CollectionTable.__tablename__} WHERE \"id\" = '{id}'"))
        if result is None or len(result) == 0:
            new_collection.id = id
            break
        
        if i == 99:
            raise ValueError("Could not find a unique id for the collection")
    
    new_collection.layer_name = layer_name
    collection_title = base_id.replace("-", " ")
    collection_title = " ".join(word.capitalize() for word in collection_title.split(" "))
    new_collection.title = collection_title
    new_collection.connection_uuid = UUID(connection_uuid)
    
    app_url_root = request.url_root.removesuffix(os.getenv("DASHBOARD_URL", "dashboard") + "/")
    
    json_link_data = {
        "url": f"{app_url_root}features/collections/{new_collection.id}/items",
        "rel": "items",
        "type": "application/geo+json",
        "title": collection_title
    }
    
    html_link_data = {
        "url": f"{app_url_root}features/collections/{new_collection.id}/items.html",
        "rel": "items",
        "type": "text/html",
        "title": collection_title
    }
    
    new_collection.links_json = generate_link([json_link_data, html_link_data])
    
    return new_collection

def create_collection(form: dict, connection_string: str = None, dataset: gdal.Dataset = None):
    if connection_string is None:    
        connection: Connection = Database.select_sqlite_db(table_model=Connection, primary_key_value=form["uuid"])
        connection_string = Database.get_postgresql_connection_string(connection.model_dump())
    
    count_existing_collection = Database.select_sqlite_db(text(f" Count(*) FROM {CollectionTable.__tablename__} WHERE \"layer_name\" = '{form['layer_name']}' AND \"connection_uuid\" = '{UUID(form['uuid']).hex}'"))
    if count_existing_collection is not None and count_existing_collection[0] > 0:
        raise ValueError(f"Collection with layer name {form['layer_name']} already exists for this connection.")
    
    if dataset is None:
        with gdal.OpenEx(connection_string) as dataset:
            new_collection = generate_collection_table_object(form["layer_name"], form["uuid"], dataset)
    else:
        new_collection = generate_collection_table_object(form["layer_name"], form["uuid"], dataset)
    
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