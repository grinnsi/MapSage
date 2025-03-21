# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil
import markdown

from server.database.db import Database
from server.ogc_apis import ogc_api_config
from server.ogc_apis.features.apis.data_api_base import BaseDataApi
import server.ogc_apis.features.implementation as implementation
import server.ogc_apis.features.implementation.subclasses.data_api

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
    Request,
    Response,
    Security,
    status,
)

from server.ogc_apis.features.models.extra_models import TokenModel  # noqa: F401
from pydantic import BeforeValidator, Field, StrictFloat, StrictInt, StrictStr
from typing import Any, List, Optional, Union
from typing_extensions import Annotated
from server.ogc_apis.features.models.exception import Exception
from server.ogc_apis.features.models.feature_collection_geo_json import FeatureCollectionGeoJSON
from server.ogc_apis.features.models.feature_geo_json import FeatureGeoJSON
from server.ogc_apis.features.models.exception import Exception as OGCException

router = APIRouter()

ns_pkg = implementation
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)

# FIXME: Use ogc Exception model for error 404
@router.get(
    "/collections/{collectionId}/items/{featureId}",
    responses={
        200: {
            "model": FeatureGeoJSON,
            "content": {
                "application/geo+json": {
                    "description": "GeoJSON representation of the feature with id `featureId` in the feature collection with id `collectionId`.",
                    "example": {
                        "type": "Feature",
                        "links": [
                            {
                                "href": "http://data.example.com/id/building/123",
                                "rel": "canonical",
                                "title": "canonical URI of the building"
                            },
                            {
                                "href": "http://data.example.com/collections/buildings/items/123.json",
                                "rel": "self",
                                "type": "application/geo+json",
                                "title": "this document"
                            },
                            {
                                "href": "http://data.example.com/collections/buildings/items/123.html",
                                "rel": "alternate",
                                "type": "text/html",
                                "title": "this document as HTML"
                            },
                            {
                                "href": "http://data.example.com/collections/buildings",
                                "rel": "collection",
                                "type": "application/geo+json",
                                "title": "the collection document"
                            }
                        ],
                        "id": "123",
                        "geometry": {
                            "type": "Polygon",
                            "coordinates": [
                            "..."
                            ]
                        },
                        "properties": {
                            "function": "residential",
                            "floors": "2",
                            "lastUpdate": "2015-08-01T12:34:56Z"
                        }
                    }
                },
                "text/html": {
                    "description": "HTML representation of the feature with id `featureId` in the feature collection with id `collectionId`.",
                    "example": "string",
                }
            },
            "description": "fetch the feature with id `featureId` in the feature collection with id `collectionId`"
        },
        404: {
            "model": OGCException,
            "content": {
                "application/json": {
                    "example": {
                        "code": 404,
                        "description": "The requested resource does not exist on the server. For example, a path parameter had an incorrect value.",
                    }
                },
                "text/html": {
                    "example": "string",
                },
            },
            "description": "The requested resource does not exist on the server. For example, a path parameter had an incorrect value."
        },
    },
    tags=["Data"],
    summary="fetch a single feature",
    response_model_by_alias=True,
    response_model_exclude_none=True,
    response_class=ogc_api_config.formats.GeoJSONResponse,
)
async def get_feature(
    *,
    collectionId: Annotated[StrictStr, Field(description="local identifier of a collection")] = Path(..., description=markdown.markdown("local identifier of a collection")),
    featureId: Annotated[StrictStr, Field(description="local identifier of a feature")] = Path(..., description=markdown.markdown("local identifier of a feature")),
    crs: Annotated[Optional[StrictStr], Field(description="The optional `crs` parameter is used to specify the coordinate reference system of the geometries in the response document. The value of the parameter is a URI identifying the coordinate reference system.  If the parameter is omitted, the default coordinate reference system  http://www.opengis.net/def/crs/OGC/1.3/CRS84 for 2D or http://www.opengis.net/def/crs/OGC/0/CRS84h for 3D is used.")] = Query(None, description=markdown.markdown("The optional `crs` parameter is used to specify the coordinate reference system of the geometries in the response document. The value of the parameter is a URI identifying the coordinate reference system.  If the parameter is omitted, the default coordinate reference system  http://www.opengis.net/def/crs/OGC/1.3/CRS84 for 2D or http://www.opengis.net/def/crs/OGC/0/CRS84h for 3D is used."), alias="crs"),
    format: ogc_api_config.ReturnFormat = Depends(ogc_api_config.params.get_format_query),
    request: Request,
    session = Depends(Database.get_sqlite_session),
) -> FeatureGeoJSON:
    """Fetch the feature with id `featureId` in the feature collection with id `collectionId`.  Use content negotiation to request HTML or GeoJSON."""
    if not BaseDataApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDataApi.subclasses[0]().get_feature(collectionId, featureId, crs, format, request, session)


@router.get(
    "/collections/{collectionId}/items",
    responses={
        200: {
            "model": FeatureCollectionGeoJSON,
            "content": {
                "application/geo+json": {
                    "description": "GeoJSON representation of the features in the feature collection with id `collectionId`.",
                    "example": {
                        "type": "FeatureCollection",
                        "links": [
                            {
                                "href": "http://data.example.com/collections/buildings/items.json",
                                "rel": "self",
                                "type": "application/geo+json",
                                "title": "this document"
                            },
                            {
                                "href": "http://data.example.com/collections/buildings/items.html",
                                "rel": "alternate",
                                "type": "text/html",
                                "title": "this document as HTML"
                            },
                            {
                                "href": "http://data.example.com/collections/buildings/items.json&offset=10&limit=2",
                                "rel": "next",
                                "type": "application/geo+json",
                                "title": "next page"
                            }
                        ],
                        "timeStamp": "2018-04-03T14:52:23Z",
                        "numberMatched": 123,
                        "numberReturned": 2,
                        "features": [
                            {
                                "type": "Feature",
                                "id": "123",
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [
                                    "..."
                                    ]
                            },
                                "properties": {
                                    "function": "residential",
                                    "floors": "2",
                                    "lastUpdate": "2015-08-01T12:34:56Z"
                                }
                            },
                            {
                                "type": "Feature",
                                "id": "132",
                                "geometry": {
                                    "type": "Polygon",
                                    "coordinates": [
                                    "..."
                                    ]
                                },
                                "properties": {
                                    "function": "public use",
                                    "floors": "10",
                                    "lastUpdate": "2013-12-03T10:15:37Z"
                                }
                            }
                        ]
                    }
                },
                "text/html": {
                    "description": "HTML representation of the features in the feature collection with id `collectionId`.",
                    "example": "string",
                },
            },
            "description": "The response is a document consisting of features in the collection. The features included in the response are determined by the server based on the query parameters of the request. To support access to larger collections without overloading the client, the API supports paged access with links to the next page if more features are selected that the page size.\n\n  The `bbox` and `datetime` parameter can be used to select only a subset of the features in the collection (the features that are in the bounding box or time interval). The `bbox` parameter matches all features in the collection that are not associated with a location, too. The `datetime` parameter matches all features in the collection that are not associated with a time stamp or interval, too.\n\n  The `limit` parameter may be used to control the subset of the selected features that should be returned in the response, the page size. Each page may include information about the number of selected and returned features (`numberMatched` and `numberReturned`) as well as links to support paging (link relation `next`)."
        },
        404: {
            "model": OGCException,
            "content": {
                "application/json": {
                    "example": {
                        "code": 404,
                        "description": "The requested resource does not exist on the server. For example, a path parameter had an incorrect value.",
                    }
                },
                "text/html": {
                    "example": "string",
                },
            },
            "description": "The requested resource does not exist on the server. For example, a path parameter had an incorrect value."
        },
    },
    tags=["Data"],
    summary="fetch features",
    response_model_by_alias=True,
    response_model_exclude_none=True,
    response_class=ogc_api_config.formats.GeoJSONResponse,
)
async def get_features(
    *,
    collectionId: Annotated[StrictStr, Field(description="local identifier of a collection")] = Path(..., description=markdown.markdown("local identifier of a collection")),
    limit: Annotated[Optional[Annotated[int, Field(le=ogc_api_config.params.LIMIT_MAXIMUM, ge=1), BeforeValidator(ogc_api_config.params.validate_limit)]], Field(description=f"The optional limit parameter limits the number of items that are presented in the response document.  Only items are counted that are on the first level of the collection in the response document. Nested objects contained within the explicitly requested items shall not be counted.  Minimum = 1. Maximum = {ogc_api_config.params.LIMIT_MAXIMUM}. Default = 100.")] = Query(100, description=markdown.markdown(f"The optional limit parameter limits the number of items that are presented in the response document.\n\n  Only items are counted that are on the first level of the collection in the response document. Nested objects contained within the explicitly requested items shall not be counted. \n\n  Minimum &#x3D; 1. Maximum &#x3D; {ogc_api_config.params.LIMIT_MAXIMUM}. Default &#x3D; 100."), alias="limit", ge=1, le=ogc_api_config.params.LIMIT_MAXIMUM),
    offset: Annotated[Optional[Annotated[int, Field(default=0, ge=0)]], Field(description="The optional offset parameter is used to skip the specified number of items in the result set. The offset is applied after the limit parameter. The first element has the index 0.")] = Query(0, description="The optional offset parameter is used to skip the specified number of items in the result set. The offset is applied after the limit parameter. The first element has the index 0.", alias="offset", ge=0),
    bbox: Annotated[Optional[Annotated[List[Union[StrictFloat, StrictInt]], BeforeValidator(ogc_api_config.params.validate_bbox)]], Field(description="Only features that have a geometry that intersects the bounding box are selected. The bounding box is provided as four or six numbers, depending on whether the coordinate reference system includes a vertical axis (height or depth):  * Lower left corner, coordinate axis 1 * Lower left corner, coordinate axis 2 * Minimum value, coordinate axis 3 (optional) * Upper right corner, coordinate axis 1 * Upper right corner, coordinate axis 2 * Maximum value, coordinate axis 3 (optional)  If the value consists of four numbers, the coordinate reference system is WGS 84 longitude/latitude (http://www.opengis.net/def/crs/OGC/1.3/CRS84) unless a different coordinate reference system is specified in the parameter `bbox-crs`.  If the value consists of six numbers, the coordinate reference system is WGS 84 longitude/latitude/ellipsoidal height (http://www.opengis.net/def/crs/OGC/0/CRS84h) unless a different coordinate reference system is specified in the parameter `bbox-crs`.  The query parameter `bbox-crs` is specified in OGC API - Features - Part 2: Coordinate Reference Systems by Reference.  For WGS 84 longitude/latitude the values are in most cases the sequence of minimum longitude, minimum latitude, maximum longitude and maximum latitude. However, in cases where the box spans the antimeridian the first value (west-most box edge) is larger than the third value (east-most box edge).  If the vertical axis is included, the third and the sixth number are the bottom and the top of the 3-dimensional bounding box.  If a feature has multiple spatial geometry properties, it is the decision of the server whether only a single spatial geometry property is used to determine the extent or all relevant geometries.")] = Query(None, description=markdown.markdown("Only features that have a geometry that intersects the bounding box are selected. The bounding box is provided as four or six numbers, depending on whether the coordinate reference system includes a vertical axis (height or depth):\n\n  * Lower left corner, coordinate axis 1\n\n * Lower left corner, coordinate axis 2\n\n * Minimum value, coordinate axis 3 (optional)\n\n * Upper right corner, coordinate axis 1\n\n * Upper right corner, coordinate axis 2\n\n * Maximum value, coordinate axis 3 (optional)\n\n  If the value consists of four numbers, the coordinate reference system is WGS 84 longitude/latitude (http://www.opengis.net/def/crs/OGC/1.3/CRS84) unless a different coordinate reference system is specified in the parameter `bbox-crs`.\n\n  If the value consists of six numbers, the coordinate reference system is WGS 84 longitude/latitude/ellipsoidal height (http://www.opengis.net/def/crs/OGC/0/CRS84h) unless a different coordinate reference system is specified in the parameter `bbox-crs`.\n\n  The query parameter `bbox-crs` is specified in OGC API - Features - Part 2: Coordinate Reference Systems by Reference.\n\n  For WGS 84 longitude/latitude the values are in most cases the sequence of minimum longitude, minimum latitude, maximum longitude and maximum latitude. However, in cases where the box spans the antimeridian the first value (west-most box edge) is larger than the third value (east-most box edge).\n\n  If the vertical axis is included, the third and the sixth number are the bottom and the top of the 3-dimensional bounding box.\n\n  If a feature has multiple spatial geometry properties, it is the decision of the server whether only a single spatial geometry property is used to determine the extent or all relevant geometries."), alias="bbox"),
    datetime: Annotated[Optional[StrictStr], Field(description="Either a date-time or an interval. Date and time expressions adhere to RFC 3339. Intervals may be bounded or half-bounded (double-dots at start or end).  Examples:  * A date-time: \"2018-02-12T23:20:50Z\" * A bounded interval: \"2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\" * Half-bounded intervals: \"2018-02-12T00:00:00Z/..\" or \"../2018-03-18T12:31:12Z\"  Only features that have a temporal property that intersects the value of `datetime` are selected.  If a feature has multiple temporal properties, it is the decision of the server whether only a single temporal property is used to determine the extent or all relevant temporal properties.")] = Query(None, description=markdown.markdown("Either a date-time or an interval. Date and time expressions adhere to RFC 3339. Intervals may be bounded or half-bounded (double-dots at start or end).\n\n  Examples:\n\n  * A date-time: \"2018-02-12T23:20:50Z\"\n\n * A bounded interval: \"2018-02-12T00:00:00Z/2018-03-18T12:31:12Z\"\n\n * Half-bounded intervals: \"2018-02-12T00:00:00Z/..\" or \"../2018-03-18T12:31:12Z\"\n\n  Only features that have a temporal property that intersects the value of `datetime` are selected.\n\n  If a feature has multiple temporal properties, it is the decision of the server whether only a single temporal property is used to determine the extent or all relevant temporal properties."), alias="datetime"),
    bbox_crs: Annotated[Optional[StrictStr], Field(description="The optional `bbox-crs` parameter is used to specify the coordinate reference system of the bounding box. The value of the parameter is a URI identifying the coordinate reference system.  If the parameter is omitted, the default coordinate reference system http://www.opengis.net/def/crs/OGC/1.3/CRS84 for 2D or http://www.opengis.net/def/crs/OGC/0/CRS84h for 3D is used.")] = Query(None, description=markdown.markdown("The optional `bbox-crs` parameter is used to specify the coordinate reference system of the bounding box. The value of the parameter is a URI identifying the coordinate reference system.\n\n  If the parameter is omitted, the default coordinate reference system http://www.opengis.net/def/crs/OGC/1.3/CRS84 for 2D or http://www.opengis.net/def/crs/OGC/0/CRS84h for 3D is used."), alias="bbox-crs"),
    crs: Annotated[Optional[StrictStr], Field(description="The optional `crs` parameter is used to specify the coordinate reference system of the geometries in the response document. The value of the parameter is a URI identifying the coordinate reference system.  If the parameter is omitted, the default coordinate reference system  http://www.opengis.net/def/crs/OGC/1.3/CRS84 for 2D or http://www.opengis.net/def/crs/OGC/0/CRS84h for 3D is used.")] = Query(None, description=markdown.markdown("The optional `crs` parameter is used to specify the coordinate reference system of the geometries in the response document. The value of the parameter is a URI identifying the coordinate reference system.\n\n  If the parameter is omitted, the default coordinate reference system  http://www.opengis.net/def/crs/OGC/1.3/CRS84 for 2D or http://www.opengis.net/def/crs/OGC/0/CRS84h for 3D is used."), alias="crs"),
    format: ogc_api_config.ReturnFormat = Depends(ogc_api_config.params.get_format_query),
    request: Request,
    session = Depends(Database.get_sqlite_session),
) -> FeatureCollectionGeoJSON:
    """Fetch features of the feature collection with id `collectionId`.  Every feature in a dataset belongs to a collection. A dataset may consist of multiple feature collections. A feature collection is often a collection of features of a similar type, based on a common schema.  Use content negotiation to request HTML or GeoJSON."""
    if not BaseDataApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseDataApi.subclasses[0]().get_features(collectionId, limit, bbox, datetime, bbox_crs, crs)
