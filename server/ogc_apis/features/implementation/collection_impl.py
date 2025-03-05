from uuid import UUID
from sqlmodel import text
from server.database.db import Database
from server.database.models import CollectionTable
from server.ogc_apis.features.implementation.static_content.pre_render import generate_link
from server.utils.crs_identifier import get_uri_of_spatial_ref
import orjson, math

from osgeo import gdal, ogr, osr

from server.utils.string_utils import string_to_kebab


def generate_collection_table_object(layer_name: str, connection_uuid: str, dataset: gdal.Dataset, app_base_url: str) -> CollectionTable:
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
    
    result = Database.select_sqlite_db(statement=text(f"SELECT id FROM {CollectionTable.__tablename__} WHERE \"id\" = '{base_id}'"))
    if result is None or len(result) == 0:
        new_collection.id = base_id
    else:
        query = f"""
            SELECT MAX(CAST(SUBSTR(id, LENGTH('{base_id}') + 2) AS INTEGER)) 
            FROM {CollectionTable.__tablename__}
            WHERE id LIKE '{base_id}' || '-%' AND SUBSTR(id, LENGTH('{base_id}') + 2) GLOB '[0-9]*'
        """
        result = Database.select_sqlite_db(statement=text(query))[0][0]
        
        next_suffix = result + 1 if result is not None else 1
        if next_suffix > 99:
            raise ValueError(f"Too many collections with the same base id {base_id}")
        
        new_collection.id = f"{base_id}-{next_suffix:02d}"
    
    new_collection.layer_name = layer_name
    collection_title = base_id.replace("-", " ")
    collection_title = " ".join(word.capitalize() for word in collection_title.split(" "))
    new_collection.title = collection_title
    new_collection.connection_uuid = UUID(connection_uuid)

    app_base_url = app_base_url.rstrip("/")
    
    json_link_data = {
        "url": f"{app_base_url}/features/collections/{new_collection.id}/items",
        "rel": "items",
        "type": "application/geo+json",
        "title": collection_title
    }
    
    html_link_data = {
        "url": f"{app_base_url}/features/collections/{new_collection.id}/items.html",
        "rel": "items",
        "type": "text/html",
        "title": collection_title
    }
    
    new_collection.links_json = generate_link([json_link_data, html_link_data])
    
    return new_collection