import uuid as unique_id
from sqlmodel import text
from server.database.db import Database
from server.database import models
from server.ogc_apis.features.models.extent import Extent
from server.ogc_apis.features.models.extent_spatial import ExtentSpatial
from server.ogc_apis.features.models.extent_temporal import ExtentTemporal
from server.utils import gdal_utils
import math, datetime, sqlmodel

from osgeo import gdal, ogr, osr

from server.utils.string_utils import string_to_kebab

def generate_collection_table_object(layer_name: str, dataset_uuid: str, dataset: gdal.Dataset, app_base_url: str, optional_data: dict = {}) -> models.CollectionTable:
    gdal.UseExceptions()
    
    new_collection = models.CollectionTable()
    
    driver: gdal.Driver = dataset.GetDriver()
    layer: ogr.Layer = dataset.GetLayerByName(layer_name)
    if layer is None:
        raise ValueError(f"Layer {layer_name} not found in dataset {dataset.GetDescription()}")
    
    spatial_ref: osr.SpatialReference = layer.GetSpatialRef()
    if spatial_ref is None:
        raise ValueError(f"Layer {layer_name} has no spatial reference")
    
    spatial_ref_uri = gdal_utils.get_uri_of_spatial_ref(spatial_ref)
    default_crs_uri = ""
    extent_coordinate_count = 4
    
    # Try to calculate bbox as 3D, just in case it is a 3D layer
    try:
        # This doesnt work 3D postgresql layer, 2D but not 3D for whatever reason
        # It seems like GDAL doesnt call the ST_3DExtent function, but the ST_Extent function, since the error mentions "BOX(..,..,..,..) is not valid 3D" ort something
        extent_calc: tuple[float] = layer.GetExtent3D(True)
    except RuntimeError as error:
        # If that fails, the extent can't be calculated like that and a driver specific method is needed
        if driver is None:
            raise ValueError(f"Driver for dataset {dataset.GetDescription()} not found") from error
        
        geom_col: str = layer.GetGeometryColumn()
        test_feature: ogr.Feature = layer.GetNextFeature()
        test_geom: ogr.Geometry = test_feature.GetGeometryRef()
        is3D = bool(test_geom.Is3D())
        
        if driver.GetName() == "PostgreSQL":
            schema, table = layer_name.split(".", 1)
            if not is3D:
                sql_query = f'SELECT ST_Extent({geom_col}) as extent FROM {schema}."{table}"'
            else:
                sql_query = f'SELECT ST_3DExtent({geom_col}) as extent FROM {schema}."{table}"'
            with dataset.ExecuteSQL(sql_query) as result:
                bbox_string: str = result.GetNextFeature()["extent"]
                bbox_string = bbox_string.split("(", 1)[1].replace(")", "").split(",")
                min_point = [float(coord) for coord in bbox_string[0].split(" ")]
                max_point = [float(coord) for coord in bbox_string[1].split(" ")]
                if len(min_point) == 2:
                    min_point.append(math.inf)
                    max_point.append(-math.inf)
                    
                extent_calc = tuple([min_point[0], max_point[0], min_point[1], max_point[1], min_point[2], max_point[2]])
        else:
            raise ValueError(f"Driver {driver.GetName()} not supported for calculating extent") from error
                
    if extent_calc[4] == math.inf and extent_calc[5] == -math.inf:
        default_crs_uri = "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
    else:
        default_crs_uri = "http://www.opengis.net/def/crs/OGC/0/CRS84h"
        extent_coordinate_count = 6
        new_collection.is_3D = True
        
    # Reorder the extent to be in the order of OGC API Features
    # FIXME: Order of axis are east, north; might need to be changed if the layer is in a different order
    extent_ordered = [gdal_utils.transform_extent(spatial_ref, default_crs_uri, extent_calc[:extent_coordinate_count], return_gdal_format=False)]
    
    # Setting the spatial extent, if one exists
    if extent_ordered and len(extent_ordered[0]) >= 4:
        spatial_extent = ExtentSpatial(bbox=extent_ordered, crs=default_crs_uri)
    else:
        spatial_extent = None
    
    # Setting the temporal extent, if an attribute field is provided in the optional data
    if "selected_date_time_field" in optional_data and optional_data["selected_date_time_field"]:
        default_trs_uri = "http://www.opengis.net/def/uom/ISO-8601/0/Gregorian"
        feature_defn: ogr.FeatureDefn = layer.GetLayerDefn()
        field_defn: ogr.FieldDefn = feature_defn.GetFieldDefn(optional_data["selected_date_time_field"])
        if not field_defn:
            raise ValueError(f"Field {optional_data['selected_date_time_field']} not found in layer {layer_name}")
        
        if field_defn.GetType() == ogr.OFTTime:
            if driver.GetName() == "PostgreSQL":
                sql_query = f"""SELECT (DATE '1970-01-01' + MIN("{optional_data["selected_date_time_field"]}"))::timestamp as min_datetime, (DATE '1970-01-01' + MAX("{optional_data["selected_date_time_field"]}"))::timestamp as max_datetime FROM """
            else:
                sql_query = f"""SELECT datetime('1970-01-01' || 'T' || (MIN("{optional_data["selected_date_time_field"]}"))) as min_datetime, datetime('1970-01-01' || 'T' || (MAX("{optional_data["selected_date_time_field"]}"))) as max_datetime FROM """
        else:
            # Not tested since no other driver than PostgreSQL is allowed at the moment
            sql_query = f'SELECT MIN("{optional_data["selected_date_time_field"]}")::timestamp as min_datetime, MAX("{optional_data["selected_date_time_field"]}")::timestamp as max_datetime FROM '
            
        if driver.GetName() == "PostgreSQL":
            schema, table = layer_name.split(".", 1)
            sql_query += f'"{schema}"."{table}"'
        else:
            sql_query += f'"{layer_name}"'
        
        with dataset.ExecuteSQL(sql_query) as result_layer:
            result: ogr.Feature = result_layer.GetNextFeature()
            min_datetime = result.GetFieldAsDateTime("min_datetime")
            max_datetime = result.GetFieldAsDateTime("max_datetime")
            
            # Currently ignores potential timezones
            min_datetime = datetime.datetime(*min_datetime[:5], second=round(min_datetime[5]))
            max_datetime = datetime.datetime(*max_datetime[:5], second=round(max_datetime[5]))

            temporal_extent = ExtentTemporal(trs=default_trs_uri, interval=[[min_datetime.isoformat(), max_datetime.isoformat()]])
        new_collection.date_time_field = optional_data["selected_date_time_field"]
    else:
        temporal_extent = None
        new_collection.date_time_field = None
        
    extent = Extent(spatial=spatial_extent, temporal=temporal_extent)
    new_collection.extent_json = extent.to_json()
    # new_collection.spatial_extent_crs = default_crs_uri
    # new_collection.temporal_extent_trs = default_trs_uri
    
    crs_list = list(set([default_crs_uri, spatial_ref_uri]))
    new_collection.crs_json = crs_list
    new_collection.storage_crs = spatial_ref_uri
    
    if spatial_ref.IsDynamic():
        new_collection.storage_crs_coordinate_epoch = spatial_ref.GetCoordinateEpoch()
    
    base_id = string_to_kebab(layer_name.split(".", 1)[-1])
    
    result = Database.select_sqlite_db(statement=text(f"SELECT id FROM {models.CollectionTable.__tablename__} WHERE \"id\" = '{base_id}'"))
    if result is None or len(result) == 0:
        new_collection.id = base_id
    else:
        query = f"""
            SELECT MAX(CAST(SUBSTR(id, LENGTH('{base_id}') + 2) AS INTEGER)) 
            FROM {models.CollectionTable.__tablename__}
            WHERE id LIKE '{base_id}' || '-%' AND SUBSTR(id, LENGTH('{base_id}') + 2) GLOB '[0-9]*'
        """
        result = Database.select_sqlite_db(statement=text(query))[0][0]
        
        next_suffix = result + 1 if result is not None else 1
        if next_suffix > 99:
            raise ValueError(f"Too many collections with the same base id {base_id}")
        
        new_collection.id = f"{base_id}-{next_suffix:02d}"
    
    new_collection.layer_name = layer_name
    collection_title = string_to_kebab(layer_name.split(".", 1)[-1]).replace("-", " ")
    collection_title = " ".join(word.capitalize() for word in collection_title.split(" "))
    new_collection.title = collection_title

    if type(dataset_uuid) is str:
        dataset_uuid = unique_id.UUID(dataset_uuid)
    new_collection.dataset_uuid = dataset_uuid
    
    for key, value in optional_data.items():
        if hasattr(new_collection, key):
            if key == "uuid" and type(value) is str:
                value = unique_id.UUID(value)
            setattr(new_collection, key, value)
    
    new_collection.pre_render(app_base_url=app_base_url)

    return new_collection

def get_collection_by_id(id: str, session: sqlmodel.Session = None) -> list[models.CollectionTable]:
    statement = sqlmodel.select(models.CollectionTable).where(models.CollectionTable.id == id)
    found_collections: list[models.CollectionTable]
    
    if session is None:
        found_collections = Database.select_sqlite_db(statement=statement)
    else:
        found_collections = session.exec(statement=statement).all()
        
    return found_collections