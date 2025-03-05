from osgeo.osr import SpatialReference

def get_code_and_authority_of_spatial_ref(spatial_ref: SpatialReference) -> tuple[str, str]:
    if spatial_ref is None:
        raise ValueError("Spatial reference is None")
    
    authority = spatial_ref.GetAuthorityName(None)
    if authority is None:
        raise ValueError("Spatial reference has no authority name")
    
    code = spatial_ref.GetAuthorityCode(None)
    if code is None:
        raise ValueError("Spatial reference has no authority code")
    
    return code, authority

def get_uri_of_spatial_ref(spatial_ref: SpatialReference) -> str:
    code, authority = get_code_and_authority_of_spatial_ref(spatial_ref)
    
    return f"http://www.opengis.net/def/crs/{authority}/0/{code}"

def get_urn_of_spatial_ref(spatial_ref: SpatialReference) -> str:
    code, authority = get_code_and_authority_of_spatial_ref(spatial_ref)
    
    return f"urn:ogc:def:crs:{authority}::{code}"