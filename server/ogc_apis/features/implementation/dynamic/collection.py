from uuid import UUID
from sqlmodel import text
from server.database.db import Database
from server.database.models import CollectionTable
from server.ogc_apis.features.models.extent import Extent
from server.ogc_apis.features.models.extent_spatial import ExtentSpatial
from server.ogc_apis.features.models.extent_temporal import ExtentTemporal
from server.utils import gdal_utils
import math

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
    
    uri_of_spatial_ref = gdal_utils.get_uri_of_spatial_ref(spatial_ref)
    default_uri_of_crs = ""
    extent_coordinate_count = 4
    
    # Always calculate the bbx as 3D, just in case it is a 3D layer
    extent_calc: tuple[float] = layer.GetExtent3D()
    if extent_calc[4] == math.inf and extent_calc[5] == -math.inf:
        default_uri_of_crs = "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
    else:
        default_uri_of_crs = "http://www.opengis.net/def/crs/OGC/0/CRS84h"
        extent_coordinate_count = 6
        
    # Reorder the extent to be in the order of OGC API Features
    # FIXME: Order of axis are east, north; might need to be changed if the layer is in a different order
    extent_ordered = [gdal_utils.transform_extent(spatial_ref, default_uri_of_crs, extent_calc[:extent_coordinate_count], return_gdal_format=False)]
    
    # Setting the spatial extent, if one exists
    if extent_ordered and len(extent_ordered[0]) >= 4:
        spatial_extent = ExtentSpatial(bbox=extent_ordered, crs=default_uri_of_crs)
    else:
        spatial_extent = None
    
    # Here we assume that the layer is NEVER temporal, and we will need to change this in the future
    if True:
        temporal_extent = None
    extent = Extent(spatial=spatial_extent, temporal=temporal_extent)
    new_collection.extent_json = extent.to_json()
    new_collection.spatial_extent_crs = uri_of_spatial_ref
    # new_collection.temporal_extent_trs = "http://www.opengis.net/def/uom/ISO-8601/0/Gregorian"
    
    crs_list = list(set([default_uri_of_crs, uri_of_spatial_ref]))
    new_collection.crs_json = crs_list
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
    
    new_collection.pre_render(app_base_url=app_base_url)

    return new_collection