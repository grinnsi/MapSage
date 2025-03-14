from osgeo import ogr, osr

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
    
    if t_srs_resource.startswith("urn"):
        t_srs = gdal_utils.get_spatial_ref_from_urn(t_srs_resource)
    else:
        t_srs = gdal_utils.get_spatial_ref_from_uri(t_srs_resource)
        
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