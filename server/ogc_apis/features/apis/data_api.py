# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil
import markdown

from server.ogc_apis.features.apis.data_api_base import BaseDataApi
import implementation

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Response,
    Security,
    status,
)

from server.ogc_apis.features.models.extra_models import TokenModel  # noqa: F401
from pydantic import Field, StrictFloat, StrictInt, StrictStr
from typing import Any, List, Optional, Union
from typing_extensions import Annotated
from server.ogc_apis.features.models.exception import Exception
from server.ogc_apis.features.models.feature_collection_geo_json import FeatureCollectionGeoJSON
from server.ogc_apis.features.models.feature_geo_json import FeatureGeoJSON


router = APIRouter()

ns_pkg = implementation
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/collections/{collectionId}/items/{featureId}",
    responses={
        200: {"model": FeatureGeoJSON, "description": "fetch the feature with id `featureId` in the feature collection with id `collectionId`"},
        404: {"description": "The requested resource does not exist on the server. For example, a path parameter had an incorrect value."},
        500: {"model": Exception, "description": "A server error occurred."},
    },
    tags=["Data"],
    summary="fetch a single feature",
    response_model_by_alias=True,
    response_model_exclude_none=True,
)
async def get_feature(
    collectionId: Annotated[StrictStr, Field(description="local identifier of a collection")] = Path(..., description=markdown.markdown("local identifier of a collection")),
    featureId: Annotated[StrictStr, Field(description="local identifier of a feature")] = Path(..., description=markdown.markdown("local identifier of a feature")),
    crs: Annotated[Optional[StrictStr], Field(description="The optional `crs` parameter is used to specify the coordinate reference system of the geometries in the response document. The value of the parameter is a URI identifying the coordinate reference system.  If the parameter is omitted, the default coordinate reference system  http://www.opengis.net/def/crs/OGC/1.3/CRS84 for 2D or http://www.opengis.net/def/crs/OGC/0/CRS84h for 3D is used.")] = Query(None, description=markdown.markdown("The optional `crs` parameter is used to specify the coordinate reference system of the geometries in the response document. The value of the parameter is a URI identifying the coordinate reference system.  If the parameter is omitted, the default coordinate reference system  http://www.opengis.net/def/crs/OGC/1.3/CRS84 for 2D or http://www.opengis.net/def/crs/OGC/0/CRS84h for 3D is used."), alias="crs"),
) -> FeatureGeoJSON:
    """Fetch the feature with id `featureId` in the feature collection with id `collectionId`.  Use content negotiation to request HTML or GeoJSON."""
    if not BaseDataApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDataApi.subclasses[0]().get_feature(collectionId, featureId, crs)


@router.get(
    "/collections/{collectionId}/items",
    responses={
        200: {"model": FeatureCollectionGeoJSON, "description": "The response is a document consisting of features in the collection. The features included in the response are determined by the server based on the query parameters of the request. To support access to larger collections without overloading the client, the API supports paged access with links to the next page, if more features are selected that the page size.  The `bbox` and `datetime` parameter can be used to select only a subset of the features in the collection (the features that are in the bounding box or time interval). The `bbox` parameter matches all features in the collection that are not associated with a location, too. The `datetime` parameter matches all features in the collection that are not associated with a time stamp or interval, too.  The `limit` parameter may be used to control the subset of the selected features that should be returned in the response, the page size. Each page may include information about the number of selected and returned features (`numberMatched` and `numberReturned`) as well as links to support paging (link relation `next`)."},
        400: {"model": Exception, "description": "A query parameter has an invalid value."},
        404: {"description": "The requested resource does not exist on the server. For example, a path parameter had an incorrect value."},
        500: {"model": Exception, "description": "A server error occurred."},
    },
    tags=["Data"],
    summary="fetch features",
    response_model_by_alias=True,
    response_model_exclude_none=True,
)
async def get_features(
    collectionId: Annotated[StrictStr, Field(description="local identifier of a collection")] = Path(..., description=markdown.markdown("local identifier of a collection")),
    limit: Annotated[Optional[Annotated[int, Field(le=10000, strict=True, ge=1)]], Field(description="The optional limit parameter limits the number of items that are presented in the response document.  Only items are counted that are on the first level of the collection in the response document. Nested objects contained within the explicitly requested items shall not be counted.  Minimum = 1. Maximum = 10000. Default = 10.")] = Query(10, description=markdown.markdown("The optional limit parameter limits the number of items that are presented in the response document.  Only items are counted that are on the first level of the collection in the response document. Nested objects contained within the explicitly requested items shall not be counted.  Minimum &#x3D; 1. Maximum &#x3D; 10000. Default &#x3D; 10."), alias="limit", ge=1, le=10000),
    bbox: Annotated[Optional[List[Union[StrictFloat, StrictInt]]], Field(description="Only features that have a geometry that intersects the bounding box are selected. The bounding box is provided as four or six numbers, depending on whether the coordinate reference system includes a vertical axis (height or depth):  * Lower left corner, coordinate axis 1 * Lower left corner, coordinate axis 2 * Minimum value, coordinate axis 3 (optional) * Upper right corner, coordinate axis 1 * Upper right corner, coordinate axis 2 * Maximum value, coordinate axis 3 (optional)  If the value consists of four numbers, the coordinate reference system is WGS 84 longitude/latitude (http://www.opengis.net/def/crs/OGC/1.3/CRS84) unless a different coordinate reference system is specified in the parameter `bbox-crs`.  If the value consists of six numbers, the coordinate reference system is WGS 84 longitude/latitude/ellipsoidal height (http://www.opengis.net/def/crs/OGC/0/CRS84h) unless a different coordinate reference system is specified in the parameter `bbox-crs`.  The query parameter `bbox-crs` is specified in OGC API - Features - Part 2: Coordinate Reference Systems by Reference.  For WGS 84 longitude/latitude the values are in most cases the sequence of minimum longitude, minimum latitude, maximum longitude and maximum latitude. However, in cases where the box spans the antimeridian the first value (west-most box edge) is larger than the third value (east-most box edge).  If the vertical axis is included, the third and the sixth number are the bottom and the top of the 3-dimensional bounding box.  If a feature has multiple spatial geometry properties, it is the decision of the server whether only a single spatial geometry property is used to determine the extent or all relevant geometries.")] = Query(None, description=markdown.markdown("Only features that have a geometry that intersects the bounding box are selected. The bounding box is provided as four or six numbers, depending on whether the coordinate reference system includes a vertical axis (height or depth):  * Lower left corner, coordinate axis 1 * Lower left corner, coordinate axis 2 * Minimum value, coordinate axis 3 (optional) * Upper right corner, coordinate axis 1 * Upper right corner, coordinate axis 2 * Maximum value, coordinate axis 3 (optional)  If the value consists of four numbers, the coordinate reference system is WGS 84 longitude/latitude (http://www.opengis.net/def/crs/OGC/1.3/CRS84) unless a different coordinate reference system is specified in the parameter `bbox-crs`.  If the value consists of six numbers, the coordinate reference system is WGS 84 longitude/latitude/ellipsoidal height (http://www.opengis.net/def/crs/OGC/0/CRS84h) unless a different coordinate reference system is specified in the parameter `bbox-crs`.  The query parameter `bbox-crs` is specified in OGC API - Features - Part 2: Coordinate Reference Systems by Reference.  For WGS 84 longitude/latitude the values are in most cases the sequence of minimum longitude, minimum latitude, maximum longitude and maximum latitude. However, in cases where the box spans the antimeridian the first value (west-most box edge) is larger than the third value (east-most box edge).  If the vertical axis is included, the third and the sixth number are the bottom and the top of the 3-dimensional bounding box.  If a feature has multiple spatial geometry properties, it is the decision of the server whether only a single spatial geometry property is used to determine the extent or all relevant geometries."), alias="bbox"),
    datetime: Annotated[Optional[StrictStr], Field(description="Either a date-time or an interval. Date and time expressions adhere to RFC 3339. Intervals may be bounded or half-bounded (double-dots at start or end).  Examples:  * A date-time: \"2018-02-12T23:20:50Z\" * A bounded interval: \"2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\" * Half-bounded intervals: \"2018-02-12T00:00:00Z/..\" or \"../2018-03-18T12:31:12Z\"  Only features that have a temporal property that intersects the value of `datetime` are selected.  If a feature has multiple temporal properties, it is the decision of the server whether only a single temporal property is used to determine the extent or all relevant temporal properties.")] = Query(None, description=markdown.markdown("Either a date-time or an interval. Date and time expressions adhere to RFC 3339. Intervals may be bounded or half-bounded (double-dots at start or end).  Examples:  * A date-time: \&quot;2018-02-12T23:20:50Z\&quot; * A bounded interval: \&quot;2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\&quot; * Half-bounded intervals: \&quot;2018-02-12T00:00:00Z/..\&quot; or \&quot;../2018-03-18T12:31:12Z\&quot;  Only features that have a temporal property that intersects the value of `datetime` are selected.  If a feature has multiple temporal properties, it is the decision of the server whether only a single temporal property is used to determine the extent or all relevant temporal properties."), alias="datetime"),
    bbox_crs: Annotated[Optional[StrictStr], Field(description="The optional `bbox-crs` parameter is used to specify the coordinate reference system of the bounding box. The value of the parameter is a URI identifying the coordinate reference system.  If the parameter is omitted, the default coordinate reference system http://www.opengis.net/def/crs/OGC/1.3/CRS84 for 2D or http://www.opengis.net/def/crs/OGC/0/CRS84h for 3D is used.")] = Query(None, description=markdown.markdown("The optional `bbox-crs` parameter is used to specify the coordinate reference system of the bounding box. The value of the parameter is a URI identifying the coordinate reference system.  If the parameter is omitted, the default coordinate reference system http://www.opengis.net/def/crs/OGC/1.3/CRS84 for 2D or http://www.opengis.net/def/crs/OGC/0/CRS84h for 3D is used."), alias="bbox-crs"),
    crs: Annotated[Optional[StrictStr], Field(description="The optional `crs` parameter is used to specify the coordinate reference system of the geometries in the response document. The value of the parameter is a URI identifying the coordinate reference system.  If the parameter is omitted, the default coordinate reference system  http://www.opengis.net/def/crs/OGC/1.3/CRS84 for 2D or http://www.opengis.net/def/crs/OGC/0/CRS84h for 3D is used.")] = Query(None, description=markdown.markdown("The optional `crs` parameter is used to specify the coordinate reference system of the geometries in the response document. The value of the parameter is a URI identifying the coordinate reference system.  If the parameter is omitted, the default coordinate reference system  http://www.opengis.net/def/crs/OGC/1.3/CRS84 for 2D or http://www.opengis.net/def/crs/OGC/0/CRS84h for 3D is used."), alias="crs"),
) -> FeatureCollectionGeoJSON:
    """Fetch features of the feature collection with id `collectionId`.  Every feature in a dataset belongs to a collection. A dataset may consist of multiple feature collections. A feature collection is often a collection of features of a similar type, based on a common schema.  Use content negotiation to request HTML or GeoJSON."""
    if not BaseDataApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDataApi.subclasses[0]().get_features(collectionId, limit, bbox, datetime, bbox_crs, crs)
