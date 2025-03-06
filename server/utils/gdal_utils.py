from osgeo import gdal, osr

def get_code_and_authority_of_spatial_ref(spatial_ref: osr.SpatialReference) -> tuple[str, str]:
    if spatial_ref is None:
        raise ValueError("Spatial reference is None")
    
    authority = spatial_ref.GetAuthorityName(None)
    if authority is None:
        raise ValueError("Spatial reference has no authority name")
    
    code = spatial_ref.GetAuthorityCode(None)
    if code is None:
        raise ValueError("Spatial reference has no authority code")
    
    return code, authority

def get_uri_of_spatial_ref(spatial_ref: osr.SpatialReference) -> str:
    code, authority = get_code_and_authority_of_spatial_ref(spatial_ref)
    
    return f"http://www.opengis.net/def/crs/{authority}/0/{code}"

def get_urn_of_spatial_ref(spatial_ref: osr.SpatialReference) -> str:
    code, authority = get_code_and_authority_of_spatial_ref(spatial_ref)
    
    return f"urn:ogc:def:crs:{authority}::{code}"

def transform_extent(source_spatial_ref: osr.SpatialReference | str, target_spatial_ref: osr.SpatialReference | str, extent: list[float], return_gdal_format: bool = True) -> list[float]:
    """
    Transforms the extent from the source spatial reference to the target spatial reference \n
    Extent is in order of [xmin, xmax, ymin, ymax, zmin, zmax] if 3D, else [xmin, xmax, ymin, ymax]
    """
    gdal.UseExceptions()
    
    if source_spatial_ref is None:
        raise ValueError("Source spatial reference is None")
    
    if isinstance(source_spatial_ref, str):
        url = source_spatial_ref
        source_spatial_ref = osr.SpatialReference()
        source_spatial_ref.ImportFromUrl(url)

    if target_spatial_ref is None:
        raise ValueError("Target spatial reference is None")
    
    if isinstance(target_spatial_ref, str):
        url = target_spatial_ref
        target_spatial_ref = osr.SpatialReference()
        target_spatial_ref.ImportFromUrl(url)
        
    if extent is None:
        raise ValueError("Extent is None")
    
    if len(extent) == 4:
        extent = (extent[0], extent[2], extent[1], extent[3])
    elif len(extent) == 6:
        extent = (extent[0], extent[2], extent[1], extent[3], extent[4], extent[5])
    else:
        raise ValueError("Extent must be [xmin, xmax, ymin, ymax] or [xmin, xmax, ymin, ymax, zmin, zmax]")
    
    transformation: osr.CoordinateTransformation = osr.CreateCoordinateTransformation(source_spatial_ref, target_spatial_ref)
    
    transformed_extent = transformation.TransformBounds(*extent[:4], densify_pts=21)
    if len(extent) == 6:
        min_pt = transformation.TransformPoint(extent[0], extent[1], extent[4])
        max_pt = transformation.TransformPoint(extent[2], extent[3], extent[5])
        transformed_extent = (*transformed_extent, min_pt[2], max_pt[2])
    
        if return_gdal_format:
            return (transformed_extent[0], transformed_extent[2], transformed_extent[1], transformed_extent[3], transformed_extent[4], transformed_extent[5])
        else:
            return (transformed_extent[0], transformed_extent[1], transformed_extent[4], transformed_extent[2], transformed_extent[3], transformed_extent[5])
    
    if return_gdal_format:
        return (transformed_extent[0], transformed_extent[2], transformed_extent[1], transformed_extent[3])
    else:
        return transformed_extent