import datetime
import os
import sys
from typing import Any, Optional
import uuid
import orjson
from osgeo import ogr, osr, gdal
import pyproj

from server.database import models
from server.ogc_apis.features.implementation import pre_render_helper
from server.utils import gdal_utils
from server.ogc_apis import ogc_api_config

ogr.UseExceptions()

def get_feature_by_id(dataset_wrapper: gdal_utils.DatasetWrapper, layer_name: str, feature_id: int) -> ogr.Feature:
    """Get a feature by its id from a dataset

    Args:
        dataset_wrapper (gdal_utils.DatasetWrapper): The dataset wrapper containing the dataset.
        layer_name (str): The name of the layer from which to get the feature.
        feature_id (int): The id of the feature to retrieve.

    Raises:
        RuntimeError: If the layer is not found in the dataset.
        ValueError: If the feature with given id is not found in the layer.
        
    Returns:
        ogr.Feature: The feature retrieved from the dataset.
    """
        
    with dataset_wrapper as ds:
        layer: ogr.Layer = ds.GetLayerByName(layer_name)
        if layer is None:
            raise RuntimeError(f"Layer '{layer_name}' not found in dataset '{ds.GetDescription()}'")
        
        try:
            feature: ogr.Feature = layer.GetFeature(feature_id)
        except RuntimeError as error:
            raise ValueError(f"Feature with id '{feature_id}' not found in layer '{layer_name}'") from error
        
        return feature

def transform_feature(feature: ogr.Feature, t_srs_resource: str) -> None:
    """Transform a feature in place to a new spatial reference system.

    Args:
        feature (ogr.Feature): The feature to transform.
        t_srs (str): The target spatial reference system as URI or URN.
    """
    
    geom: ogr.Geometry = feature.GetGeometryRef()
    # If the feature has no geometry, return the feature as is
    # Don't know whether this is the correct behavior
    if geom is None:        
        return
    
    t_srs = gdal_utils.get_spatial_ref_from_ressource(t_srs_resource)
        
    geom.TransformTo(t_srs)

# Could be cached with LRU cache if necessary
def generate_feature_links(base_url: str, collection_id: str, feature_id: str | int) -> list[dict[str, str]]:
    """Generate a list of links for the feature response.

    Args:
        url_path (str): The path to the feature collection.
        collection_id (str): The id of the feature collection.
        feature_id (str | int): The id of the feature.

    Returns:
        list[dict[str, str]]: A list of links for the feature collection.
    """
    
    base_url = base_url.rstrip('/')
    if isinstance(feature_id, int):
        feature_id = str(feature_id)
    
    link_self = {
        "href": f"{base_url}{ogc_api_config.routes.FEATURES}/collections/{collection_id}/items/{feature_id}",
        "rel": "self",
        "title": "This document as {format_name}"    
    }
    
    link_root = {
        "href": f"{base_url}{ogc_api_config.routes.FEATURES}",
        "rel": "root",
        "title": "Landing page of the server as {format_name}"
    }
    
    link_collection = {
        "href": f"{base_url}{ogc_api_config.routes.FEATURES}/collections/{collection_id}",
        "rel": "collection",
        "title": "The collection document as {format_name}"
    }
    
    links = pre_render_helper.generate_multiple_link_types(link_self, formats=["geojson", "html"])
    links.extend(pre_render_helper.generate_links([link_root, link_collection], multiple_types=True))
    
    return links

def get_feature_count(
    layer: ogr.Layer, 
    filter_geom: Optional[ogr.Geometry], 
    datetime_interval: tuple[Optional[datetime.datetime], Optional[datetime.datetime]],
    datetime_field: Optional[str] = None,
    sql_where_query: Optional[str] = None,
) -> int:
    """Get the number of features in a layer within a bounding box. \n
    Features without geometry (and datetime if provided) are also counted due to the OGC Specification

    Args:
        layer (ogr.Layer): The layer from which to get the number of features.
        filter_geom (Optional[ogr.Geometry]): The geometry to spatialy filter the features.
        datetime_interval (tuple[Optional[datetime.datetime], Optional[datetime.datetime]]): The datetime interval to filter features.
        datetime_field (Optional[str]): The name of the datetime field to filter features.
        sql_where_query (Optional[str]): A SQL WHERE query to filter the features. Only used for database drivers.
        count_null_geom (bool): Whether to count features with NULL geometry.

    Returns:
        int: The number of features in the layer within the filters.
    """
    
    ds: gdal.Dataset = layer.GetDataset()
    driver: gdal.Driver = ds.GetDriver()
    driver_name: str = driver.GetName()
    geom_col: str = layer.GetGeometryColumn()
    
    if driver_name == "PostgreSQL":
        # PostGIS
        schema, table = layer.GetName().split(".")  
        sql = f'SELECT COUNT(*) as count FROM "{schema}"."{table}"'
        where_clauses = []
        
        if sql_where_query:
            if "where" not in sql_where_query.lower():
                sql += " WHERE " + sql_where_query
            sql += sql_where_query
            with ds.ExecuteSQL(sql) as result:
                total_feature_count = result.GetNextFeature().GetField("count")
        else:
            if filter_geom is not None:
                with ds.ExecuteSQL(f"SELECT Find_SRID('{schema}','{table}','{geom_col}') as srid") as result:
                    srid = result.GetNextFeature().GetField("srid")
                
                if filter_geom.Is3D():
                    z_min = filter_geom.GetGeometryRef(0).GetZ(0)
                    z_max = filter_geom.GetGeometryRef(0).GetZ(2)
                    where_clauses.append(f'(ST_Intersects("{geom_col}", ST_GeomFromText(\'{filter_geom.ExportToWkt()}\', {srid})) AND ST_ZMin("{geom_col}") <= {z_max} AND ST_ZMax("{geom_col}") >= {z_min}) OR "{geom_col}" IS NULL')
                else:
                    filter_geom.FlattenTo2D()
                    where_clauses.append(f'ST_Intersects({geom_col}, ST_GeomFromText(\'{filter_geom.ExportToWkt()}\', {srid})) OR {geom_col} IS NULL')
            
            if datetime_interval and datetime_field:
                start, end = datetime_interval
                if start and end:
                    where_clauses.append(f'("{datetime_field}" >= \'{start.isoformat()}\' AND "{datetime_field}" <= \'{end.isoformat()}\') OR {datetime_field} IS NULL')
                elif start:
                    where_clauses.append(f'"{datetime_field}" >= \'{start.isoformat()}\' OR {datetime_field} IS NULL')
                elif end:
                    where_clauses.append(f'"{datetime_field}" <= \'{end.isoformat()}\' OR {datetime_field} IS NULL')
            
            where_clauses = [f'({clause})' for clause in where_clauses]
            sql += (" WHERE " + " AND ".join(where_clauses)) if len(where_clauses) > 0 else ""
            
            with ds.ExecuteSQL(sql) as result:
                total_feature_count = result.GetNextFeature().GetField("count")
    else:
        # File based drivers (at least GeoPackage)
        null_geom_count = 0
        if count_null_geom:
            # Get geometry column name
            geom_col = layer.GetGeometryColumn()
            if geom_col == "":
                geom_col = "_ogr_geometry_"
                
            # Count only NULL geometry features
            layer.SetAttributeFilter(f"{geom_col} IS NULL")
            null_geom_count = layer.GetFeatureCount()
            # Manually count NULL geometry features
            # for feature in layer:
            #     null_geom_count += 1
            
            layer.SetAttributeFilter(None)
            layer.ResetReading()
        
        feature_count = 0
        if filter_geom:
            layer.SetSpatialFilter(filter_geom)
            if not filter_geom.Is3D() or layer.GetSpatialRef().GetAxesCount() == 2:
                feature_count = layer.GetFeatureCount()
            else:
                filter_env = filter_geom.GetEnvelope3D()
                for feature in layer:
                    geom = feature.GetGeometryRef()
                    feature_env = geom.GetEnvelope3D()
                    if feature_env[4] > filter_env[5] or feature_env[5] < filter_env[4]:
                        continue
                    
                    feature_count += 1
            
            layer.SetSpatialFilter(None)
            layer.ResetReading()
        
        # Manually count features
        # for feature in layer:
        #     include = False
            
        #     if bbox is not None:
        #         geom: ogr.Geometry = feature.GetGeometryRef().Clone()
                
        #         if geom and geom.Intersects(filter_geom):
        #             # For Z filtering, check if the geometry's Z range overlaps with our filter
        #             # If the geometry has no Z, we count it as well since it COULD be in the bbox and the Z coordinate was frogotten to be set (OGC reasoning)
        #             if not calc_3D or not geom.Is3D():
        #                 include = True
        #             else:
        #                 env = geom.GetEnvelope3D()
        #                 if env[4] > bbox[5] or env[5] < bbox[2]:
        #                     continue
                        
        #                 include = True     
        #     else:
        #         include = True
                
        #     if include:
        #         feature_count += 1

        total_feature_count = feature_count + null_geom_count

    return total_feature_count

def prepare_features_postgresql(
    layer: ogr.Layer, 
    filter_geom: Optional[ogr.Geometry], 
    datetime_interval: tuple[Optional[datetime.datetime], Optional[datetime.datetime]], 
    datetime_field: Optional[str], 
    limit: int, 
    offset: int, 
    gdal_vector_translate_options: dict = None
) -> tuple[Any, int, int]:
    
    if filter_geom:
        filter_geom_srs = filter_geom.GetSpatialReference()
        layer_srs = layer.GetSpatialRef()
        if filter_geom_srs and layer_srs and not filter_geom_srs.IsSame(layer_srs):
            raise RuntimeError("Filter geometry and layer have different spatial reference systems")
    
    layer_name = layer.GetName()
    geom_col = layer.GetGeometryColumn()
    fid_col = layer.GetFIDColumn()
    schema, table = layer_name.split(".")
    dataset: gdal.Dataset = layer.GetDataset()
    
    with dataset.ExecuteSQL(f"SELECT Find_SRID('{schema}', '{table}', '{geom_col}') as srid") as result:
        feature = result.GetNextFeature()
        srid = feature.GetField("srid")
    
    where_clauses = []
    if filter_geom:
        if filter_geom.Is3D():
            # Cant use ST_3DIntersects with Box3D, since the Box3D would "unwarp" the filter geometry and thus would make it bigger when one system is geographic while the other is projected
            # where_clauses.append(f'ST_3DIntersects({geom_col}, Box3D(ST_GeomFromText(\'{filter_geom.ExportToWkt()}\', {srid})))')
            
            z_min = filter_geom.GetGeometryRef(0).GetZ(0)
            z_max = filter_geom.GetGeometryRef(0).GetZ(2)
            where_clauses.append(f'(ST_Intersects({geom_col}, ST_GeomFromText(\'{filter_geom.ExportToWkt()}\', {srid})) AND ST_ZMin({geom_col}) <= {z_max} AND ST_ZMax({geom_col}) >= {z_min})')
        else:
            filter_geom.FlattenTo2D()
            where_clauses.append(f'(ST_Intersects({geom_col}, ST_GeomFromText(\'{filter_geom.ExportToWkt()}\', {srid})))')
        where_clauses.append(f'({geom_col} IS NULL)')

    where_clauses = (" WHERE " + " OR ".join(where_clauses)) if len(where_clauses) > 0 else ""
    
    matched_feature_count = get_feature_count(layer, filter_geom, datetime_interval, datetime_field, sql_where_query=where_clauses)
    if offset >= matched_feature_count and matched_feature_count > 0:
        raise ValueError(f"Offset is greater than or equal to the number of features in the layer/extent")
    
    sql_statement = f'SELECT * FROM "{schema}"."{table}" {where_clauses}'
    sql_statement += f" ORDER BY {fid_col} LIMIT {limit} OFFSET {offset}"
    
    options = gdal.VectorTranslateOptions(
        **gdal_vector_translate_options,
        SQLStatement=sql_statement
    )

    return options, matched_feature_count

def prepare_features_file(
    layer: ogr.Layer, 
    filter_geom: Optional[ogr.Geometry], 
    datetime_interval: tuple[Optional[datetime.datetime], Optional[datetime.datetime]], 
    datetime_field: Optional[str], 
    limit: int, 
    offset: int, 
    gdal_vector_translate_options: dict = None
) -> tuple[Any, int, int]:
    # Needs to be redone if file based drivers become available
    
    where_clauses = []
    geom_col = layer.GetGeometryColumn()
    fid_col = layer.GetFIDColumn()
    
    matched_feature_count = get_feature_count(layer, filter_geom, datetime_interval)
    if offset >= matched_feature_count and matched_feature_count > 0:
        raise ValueError(f"Offset is greater than or equal to the number of features in the layer/extent")
    
    if filter_geom:
        filter_geom_srs = filter_geom.GetSpatialReference()
        layer_srs = layer.GetSpatialRef()
        if filter_geom_srs and layer_srs and not filter_geom_srs.IsSame(layer_srs):
            raise RuntimeError("Filter geometry and layer have different spatial reference systems")
        
        # The ST functions might only work for GeoPackages, since they have these functions implemented
        # Another approach for Shapefiles and so might be needed in the future
        query_3D_string = ""
        if filter_geom.Is3D():
            # filter_env = filter_geom.GetEnvelope3D()
            z_min = filter_geom.GetGeometryRef(0).GetZ(0)
            z_max = filter_geom.GetGeometryRef(0).GetZ(2)
            query_3D_string = f"AND ST_MinZ({geom_col}) <= {z_max} AND ST_MaxZ({geom_col}) >= {z_min}"
        filter_geom.FlattenTo2D()
        where_clauses.append(f'(ST_Intersects({geom_col}, ST_GeomFromText(\'{filter_geom.ExportToWkt()}\')) {query_3D_string})')
        where_clauses.append(f'(ST_IsEmpty({geom_col}))')
        
    sqllite_query = (
        f'SELECT * FROM "{layer.GetName()}" '
        f'WHERE {" OR ".join(where_clauses)} '
        f'ORDER BY {fid_col} LIMIT {limit} OFFSET {offset}'
    )
    
    options = gdal.VectorTranslateOptions(
        **gdal_vector_translate_options,
        SQLDialect="SQLite",
        SQLStatement=sqllite_query
    )
    
    return options, matched_feature_count    
    
    # Manuell getting and filtering of features
    # Currently not used, but might be useful in the future
    
    # layer.SetSpatialFilter(filter_geom)
    # skipped = True
    # try:
    #     layer.SetNextByIndex(offset)
    # except RuntimeError:
    #     skipped = False
        
    # returned_feature_count = 0
    # skipped_features = 0
    # features = []
    # while returned_feature_count < limit:
    #     feature: ogr.Feature = layer.GetNextFeature()
    #     if feature is None:
    #         break
        
    #     include = False
    #     geom = feature.GetGeometryRef()
        
    #     if filter_geom is not None:                    
    #         # If the geometry has no Z, we include it as well since it COULD be in the bbox and the Z coordinate was forgotten to be set (OGC reasoning)
    #         if not geom.Is3D() or not filter_geom.Is3D():
    #             include = True
    #         else:
    #             feature_env = geom.GetEnvelope3D()
    #             if feature_env[4] > filter_env[5] or feature_env[5] < filter_env[4]:
    #                 continue
                
    #             include = True
    #     else:
    #         include = True
            
    #     if include:
    #         if not skipped and skipped_features < offset:
    #             skipped_features += 1
    #             continue
            
    #         returned_feature_count += 1
    #         features.append(feature)
    
    # layer.SetSpatialFilter(None)
    # layer.ResetReading()
    
    # if returned_feature_count < limit and returned_feature_count + offset < matched_feature_count:
    #     geom_col = layer.GetGeometryColumn()
    #     if geom_col == "":
    #         geom_col = "_ogr_geometry_"
        
    #     layer.SetAttributeFilter(f"{geom_col} IS NULL")
        
    #     while returned_feature_count < limit:
    #         feature: ogr.Feature = layer.GetNextFeature()
    #         if feature is None:
    #             break
            
    #         if not skipped and skipped_features < offset:
    #             skipped_features += 1
    #             continue
            
    #         returned_feature_count += 1
    #         features.append(feature)
        
    #     layer.SetAttributeFilter(None)
    #     layer.ResetReading()
    
    # return features, matched_feature_count, returned_feature_count

def get_features(
    dataset_wrapper: gdal_utils.DatasetWrapper, 
    layer_name: str, bbox: list[float], 
    bbox_srs_res: str, 
    datetime_interval: tuple[Optional[datetime.datetime], Optional[datetime.datetime]], 
    datetime_field: Optional[str], 
    t_srs_res: str, 
    limit: int, 
    offset: int
):
    """Get features from a dataset within a bounding box.

    Args:
        dataset_wrapper (gdal_utils.DatasetWrapper): The dataset wrapper containing the dataset.
        layer_name (str): The name of the layer from which to get the features.
        bbox (list[float]): The bounding box to filter the features in format xmin, ymin, zmin, xmax, ymax, zmax.
        bbox_srs_res (str): The coordinate reference system of the bounding box as URI or URN.
        datetime_interval (tuple[Optional[datetime.datetime], Optional[datetime.datetime]]): The temporal interval to filter the features.
        datetime_field (Optional[str]): The optional field for filtering by datetime.
        t_srs_res (str): The target spatial reference system as URI or URN.
        limit (int): The maximum number of features to return.
        offset (int): The number of features to skip.

    Raises:
        ValueError: Provided parameters are invalid
        RuntimeError: If the layer is not found in the dataset.

    Returns:
        dict: A dictionary (GeoJSON) containing the features retrieved from the dataset.
        int: The total number of features in the layer with given spatial, attribute and (temporal) filter.
        int: The returned number of features in the GeoJSON object with given spatial, attribute and (temporal) filter.
    """
    ds: gdal.Dataset
    with dataset_wrapper as ds:
        try:
            layer = ds.GetLayerByName(layer_name)
        except RuntimeError as error:
            raise RuntimeError(f"Layer '{layer_name}' not found in dataset '{ds.GetDescription()}'") from error
    
    try:
        t_srs = gdal_utils.get_spatial_ref_from_ressource(t_srs_res)
    except ValueError as error:
        raise ValueError(f"Invalid target spatial reference system: {error}") from error
    
    filter_geom = None
    if bbox is not None:
        try:
            bbox_srs = gdal_utils.get_spatial_ref_from_ressource(bbox_srs_res)
        except ValueError as error:
            raise ValueError(f"Invalid bounding box spatial reference system: {error}") from error

        filter_ring = ogr.Geometry(ogr.wkbLinearRing)
        if len(bbox) == 4:
            filter_ring.AddPoint_2D(bbox[0], bbox[1])
            filter_ring.AddPoint_2D(bbox[2], bbox[1])
            filter_ring.AddPoint_2D(bbox[2], bbox[3])
            filter_ring.AddPoint_2D(bbox[0], bbox[3])
            filter_ring.AddPoint_2D(bbox[0], bbox[1])
        elif len(bbox) == 6:
            filter_ring.AddPoint(bbox[0], bbox[1], bbox[2])
            filter_ring.AddPoint(bbox[3], bbox[1], bbox[2])
            filter_ring.AddPoint(bbox[3], bbox[4], bbox[5])
            filter_ring.AddPoint(bbox[0], bbox[4], bbox[5])
            filter_ring.AddPoint(bbox[0], bbox[1], bbox[2])
        else:
            raise ValueError("Input for parameter 'bbox' of type 'query' is invalid. Input should consist of 4 or 6 values")

        filter_geom = ogr.Geometry(ogr.wkbPolygon)
        filter_geom.AddGeometry(filter_ring)
        
        filter_geom.AssignSpatialReference(bbox_srs)
        
        # Ensure the filter geometry has the same spatial reference as the layer
        layer_srs = layer.GetSpatialRef()
        if bbox_srs and layer_srs and not bbox_srs.IsSame(layer_srs):
            transform = osr.CoordinateTransformation(bbox_srs, layer_srs)
            filter_geom.Transform(transform)
    
    translate_options = {
        "format": "GeoJSON",
        "srcSRS": layer.GetSpatialRef(),
        "dstSRS": t_srs,
        "reproject": True,
        "layerCreationOptions": {
            "WRITE_NAME": False,
            "ID_FIELD": layer.GetFIDColumn(),
        },
    }
    
    driver_name = ds.GetDriver().GetName()
    with gdal.config_option("GDAL_NUM_THREADS", "ALL_CPUS"):
        if driver_name == "PostgreSQL":
            options, matched_feature_count = prepare_features_postgresql(layer, filter_geom, datetime_interval, datetime_field, limit, offset, translate_options)
        else:
            options, matched_feature_count = prepare_features_file(layer, filter_geom, datetime_interval, datetime_field, limit, offset, translate_options)
                
        file_id = uuid.uuid4()
        gdal.VectorTranslate(f"/vsimem/{file_id}.geojson", dataset_wrapper.dataset_desc, options=options)
        vsi_file = gdal.VSIFOpenL(f'/vsimem/{file_id}.geojson', 'rb')
        # Get the file size
        gdal.VSIFSeekL(vsi_file, 0, 2)  # Seek to end
        file_size = gdal.VSIFTellL(vsi_file)
        gdal.VSIFSeekL(vsi_file, 0, 0)  # Seek back to beginning
        
        # Read entire content at once
        content = gdal.VSIFReadL(1, file_size, vsi_file)
        # Process the content as needed (e.g., decode from bytes)
        geojson_object = orjson.loads(content)
        
        # Close the file
        gdal.VSIFCloseL(vsi_file)
        gdal.Unlink(f'/vsimem/{file_id}.geojson')
        
        return geojson_object, matched_feature_count, len(geojson_object["features"])

# Apparently clients like QGIS cant handle streamed data. They receive it but they only render the features after the whole response is received
# So streaming doesnt lead to a better user experience (showing more and more features until everything is finished)instead of waiting)
# I leave this function in here for the time being, but it is not used
async def stream_features(dataset_wrapper: gdal_utils.DatasetWrapper, layer_name: str, limit: int, offset: int, bbox: list[float], bbox_srs_res: str, t_srs_res: str):
    ds: gdal.Dataset
    with dataset_wrapper as ds:
        try:
            layer = ds.GetLayerByName(layer_name)
        except RuntimeError as error:
            raise RuntimeError(f"Layer '{layer_name}' not found in dataset '{ds.GetDescription()}'") from error
    
    try:
        t_srs = gdal_utils.get_spatial_ref_from_ressource(t_srs_res)
    except ValueError as error:
        raise ValueError(f"Invalid target spatial reference system: {error}") from error
    
    filter_geom = None
    if bbox is not None:
        try:
            bbox_srs = gdal_utils.get_spatial_ref_from_ressource(bbox_srs_res)
        except ValueError as error:
            raise ValueError(f"Invalid bounding box spatial reference system: {error}") from error

        filter_ring = ogr.Geometry(ogr.wkbLinearRing)
        if len(bbox) == 4:
            filter_ring.AddPoint_2D(bbox[0], bbox[1])
            filter_ring.AddPoint_2D(bbox[2], bbox[1])
            filter_ring.AddPoint_2D(bbox[2], bbox[3])
            filter_ring.AddPoint_2D(bbox[0], bbox[3])
            filter_ring.AddPoint_2D(bbox[0], bbox[1])
        elif len(bbox) == 6:
            filter_ring.AddPoint(bbox[0], bbox[1], bbox[2])
            filter_ring.AddPoint(bbox[3], bbox[1], bbox[2])
            filter_ring.AddPoint(bbox[3], bbox[4], bbox[5])
            filter_ring.AddPoint(bbox[0], bbox[4], bbox[5])
            filter_ring.AddPoint(bbox[0], bbox[1], bbox[2])
        else:
            raise ValueError("Bounding box must have 4 or 6 coordinates")

        filter_geom = ogr.Geometry(ogr.wkbPolygon)
        filter_geom.AddGeometry(filter_ring)
        
        filter_geom.AssignSpatialReference(bbox_srs)
        
        # Ensure the filter geometry has the same spatial reference as the layer
        layer_srs = layer.GetSpatialRef()
        if bbox_srs and layer_srs and not bbox_srs.IsSame(layer_srs):
            transform = osr.CoordinateTransformation(bbox_srs, layer_srs)
            filter_geom.Transform(transform)
    
    driver_name = ds.GetDriver().GetName()
    with gdal.config_option("GDAL_NUM_THREADS", "ALL_CPUS"):
        if driver_name == "PostgreSQL":
            features, matched_feature_count, returned_feature_count = prepare_features_postgresql(layer, filter_geom, limit, offset)
        else:
            features, matched_feature_count, returned_feature_count = prepare_features_file(layer, filter_geom, limit, offset)
    
        yield b'{"type":"FeatureCollection","features":['
    
        fid_col = layer.GetFIDColumn()
        buffer_size = 0.5 * 1024 * 1024  # 0.5 MB
        max_features_per_chunk = 50
        buffer = []
        current_size = 0
        
        for idx, feature in enumerate(features):
            # Transform and prepare the feature
            geom: ogr.Geometry = feature.GetGeometryRef()
            if geom:
                geom.TransformTo(t_srs)
            
            # Export feature and remove properties you don't want
            json_feature = feature.ExportToJson(as_object=True)
            if fid_col in json_feature["properties"]:
                del json_feature["properties"][fid_col]
                
            # Convert to string with proper JSON formatting
            feature_str = orjson.dumps(json_feature)
            
            # Add comma if not the first feature
            if idx > 0:
                feature_str = b"," + feature_str
                
            buffer.append(feature_str)
            current_size += sys.getsizeof(feature_str)
            
            # Yield when buffer gets large enough
            if current_size >= buffer_size or len(buffer) >= max_features_per_chunk:
                yield b"".join(buffer)
                buffer = []
                current_size = 0
        
        # Send any remaining buffered features
        if buffer:
            yield b"".join(buffer)
            
        # Complete the GeoJSON document
        import datetime as dt
        footer = f'],"numberMatched":{matched_feature_count},"numberReturned":{returned_feature_count},"timeStamp":"{dt.datetime.now().replace(microsecond=0).isoformat()}"'
        footer += '}'
        
        yield footer

def generate_features_links(base_url: str, url_self: str, url_next: str = None, url_prev: str = None) -> list[dict[str, str]]:
    links = []
    
    links.append({
        "href": f"{url_self}",
        "rel": "self",
        "title": "This document as {format_name}"
    })
    
    if url_next is not None:
        links.append({
            "href": f"{url_next}",
            "rel": "next",
            "title": "Next page of returned features as {format_name}"
        })
    
    if url_prev is not None:
        links.append({
            "href": f"{url_prev}",
            "rel": "prev",
            "title": "Previous page of returned features as {format_name}"
        })
    
    links = pre_render_helper.generate_links(links, formats=["geojson", "html"], multiple_types=True)
    
    link_root = {
        "href": f"{base_url.rstrip("/")}{ogc_api_config.routes.FEATURES}",
        "rel": "root",
        "title": "Landing page of the server as {format_name}"
    }
    
    links.extend(pre_render_helper.generate_multiple_link_types(link_root))
    
    return links