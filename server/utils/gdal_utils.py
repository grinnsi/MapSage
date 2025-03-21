from enum import Enum
import re
from osgeo import gdal, osr
import pyproj
import sqlmodel

from server.database.models import CollectionTable

gdal.UseExceptions()

def get_code_and_authority_of_spatial_ref(spatial_ref: osr.SpatialReference) -> tuple[str, str]:
    if spatial_ref is None:
        raise TypeError("Spatial reference is None")
    
    authority = spatial_ref.GetAuthorityName(None)
    if authority is None:
        raise KeyError("Spatial reference has no authority name")
    
    code = spatial_ref.GetAuthorityCode(None)
    if code is None:
        raise KeyError("Spatial reference has no authority code")
    
    return code, authority

def get_uri_of_spatial_ref(spatial_ref: osr.SpatialReference) -> str:
    code, authority = get_code_and_authority_of_spatial_ref(spatial_ref)
    
    return f"http://www.opengis.net/def/crs/{authority}/0/{code}"

def get_urn_of_spatial_ref(spatial_ref: osr.SpatialReference) -> str:
    code, authority = get_code_and_authority_of_spatial_ref(spatial_ref)
    
    return f"urn:ogc:def:crs:{authority}::{code}"

def get_spatial_ref_from_uri(uri: str) -> osr.SpatialReference:
    if uri is None:
        raise TypeError("URI is None")
    
    try:
        authority, code = re.findall(r"http://www.opengis.net/def/crs/(\w+)/[\d.]+/(.+)", uri)[0]
        wkt = pyproj.CRS.from_authority(authority, code).to_wkt()
        spatial_ref = osr.SpatialReference(wkt)

        return spatial_ref
    except Exception:
        raise ValueError("URI format is invalid or does not contain authority and code")

def get_spatial_ref_from_ressource(ressource: str) -> osr.SpatialReference:
    if ressource is None:
        raise ValueError("Resource is None")

    if ressource.startswith("http"):
        return get_spatial_ref_from_uri(ressource)
    elif ressource.startswith("urn"):
        return get_spatial_ref_from_urn(ressource)
    else:
        raise ValueError("Resource must be a valid URI or URN")

def get_spatial_ref_from_urn(urn: str) -> osr.SpatialReference:
    if urn is None:
        raise TypeError("URN is None")
    
    try:
        authority, code = re.findall(r"urn:ogc:def:crs:(\w+):[\d.]*:(.+)", urn)[0]
        wkt = pyproj.CRS.from_authority(authority, code).to_wkt()
        spatial_ref = osr.SpatialReference(wkt)

        return spatial_ref
    except Exception:
        raise ValueError("URN format is invalid or does not contain authority and code")

def get_wkt_from_uri(uri: str) -> str:
    if uri is None:
        raise TypeError("URI is None")
    
    spatial_ref = get_spatial_ref_from_uri(uri)
    
    return spatial_ref.ExportToWkt()
    
def transform_extent(source_spatial_ref: osr.SpatialReference | str, target_spatial_ref: osr.SpatialReference | str, extent: list[float], input_gdal_format: bool = True, return_gdal_format: bool = True) -> list[float]:
    """
    Transforms the extent from the source spatial reference to the target spatial reference \n
    Extent is in order of [xmin, xmax, ymin, ymax, zmin, zmax] if 3D, else [xmin, xmax, ymin, ymax] \n
    If input_gdal_format is False, the extent is expected in the order of [xmin, xmax, ymin, ymax, zmin, zmax] if 3D, else [xmin, xmax, ymin, ymax] \n
    If return_gdal_format is False, the extent is returned in the order of [xmin, ymin, zmin, xmax, ymax, zmax] if 3D, else [xmin, ymin, xmax, ymax]
    """
    
    if source_spatial_ref is None:
        raise TypeError("Source spatial reference is None")
    
    if isinstance(source_spatial_ref, str):
        uri = source_spatial_ref
        source_spatial_ref = get_spatial_ref_from_uri(uri) if uri.startswith("http") else get_spatial_ref_from_urn(uri)

    if target_spatial_ref is None:
        raise TypeError("Target spatial reference is None")
    
    if isinstance(target_spatial_ref, str):
        uri = target_spatial_ref
        target_spatial_ref = get_spatial_ref_from_uri(uri) if uri.startswith("http") else get_spatial_ref_from_urn(uri)
        
    if extent is None:
        raise TypeError("Extent is None")
    
    if len(extent) == 4:
        if input_gdal_format:
            extent = (extent[0], extent[2], extent[1], extent[3])
    elif len(extent) == 6:
        if input_gdal_format:
            extent = (extent[0], extent[2], extent[1], extent[3], extent[4], extent[5])
        else:
            extent = (extent[0], extent[1], extent[3], extent[4], extent[2], extent[5])
    else:
        raise ValueError("Extent must be [xmin, xmax, ymin, ymax] or [xmin, xmax, ymin, ymax, zmin, zmax]")
    
    transformation: osr.CoordinateTransformation = osr.CreateCoordinateTransformation(source_spatial_ref, target_spatial_ref)
    
    extent_transformed = transformation.TransformBounds(*extent[:4], 21)
    if len(extent) == 6:
        min_pt = transformation.TransformPoint(extent[0], extent[1], extent[4])
        max_pt = transformation.TransformPoint(extent[2], extent[3], extent[5])
        extent_transformed = (*extent_transformed, min_pt[2], max_pt[2])
    
        if return_gdal_format:
            return (extent_transformed[0], extent_transformed[2], extent_transformed[1], extent_transformed[3], extent_transformed[4], extent_transformed[5])
        else:
            return (extent_transformed[0], extent_transformed[1], extent_transformed[4], extent_transformed[2], extent_transformed[3], extent_transformed[5])
    
    if return_gdal_format:
        return (extent_transformed[0], extent_transformed[2], extent_transformed[1], extent_transformed[3])
    else:
        return extent_transformed

class DatasetWrapper(object):    
    dataset_desc: gdal.Dataset
    dataset_open_options: dict[str, str]
    dataset_type = Enum("DatasetType", "VECTOR RASTER")
    _flags = gdal.OF_VERBOSE_ERROR | gdal.OF_SHARED | gdal.OF_READONLY
    
    def __init__(self, dataset_desc: str, dataset_open_options: dict[str, str], dataset_type: dataset_type = dataset_type.VECTOR):
        self.dataset_desc = dataset_desc
        self.dataset_open_options = dataset_open_options
        self.dataset_type = dataset_type
        
    def __enter__(self):
        self._flags |= gdal.OF_VECTOR if self.dataset_type == self.dataset_type.VECTOR else gdal.OF_RASTER
        self.ds: gdal.Dataset = gdal.OpenEx(self.dataset_desc, self._flags, open_options=self.dataset_open_options)
        return self.ds
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Close dataset with garbage collection, by removing reference
        self.ds = None
        return False

def get_dataset_from_collection_table(collection: CollectionTable, session: sqlmodel.Session) -> DatasetWrapper:
    # Currently only supports postgis
    dataset = collection.dataset
    dataset_path = dataset.path
    # Check what type of dataset it is
    # Since it's currently only postgis, we can assume it's a connection string
    if True:
        open_options = {}
        type = DatasetWrapper.dataset_type.VECTOR
    else:
        pass
    
    return DatasetWrapper(dataset_path, open_options, type)