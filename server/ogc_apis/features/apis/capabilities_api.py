# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from fastapi.responses import ORJSONResponse
from server.database.db import Database
from server.ogc_apis import ogc_api_config
from server.ogc_apis.features.apis.capabilities_api_base import BaseCapabilitiesApi
import server.ogc_apis.features.implementation as implementation
import server.ogc_apis.features.implementation.subclasses.capabilities_api

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
from pydantic import Field, StrictStr
from typing import Any
from typing_extensions import Annotated
from server.ogc_apis.features.models.collection import Collection
from server.ogc_apis.features.models.collections import Collections
from server.ogc_apis.features.models.conf_classes import ConfClasses
from server.ogc_apis.features.models.landing_page import LandingPage
from server.ogc_apis.features.models.exception import Exception as OGCException


router = APIRouter()

ns_pkg = implementation
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/collections/{collectionId}",
    responses={
        200: {
            "model": Collection,
            "content": {
                "application/json": {
                    "description": "JSON representation of the feature collection with id `collectionId`.",
                    "example": {
                        "id": "buildings",
                        "title": "Buildings",
                        "description": "Buildings in the city of Bonn.",
                        "extent": {
                            "spatial": {
                                "bbox": [
                                    [
                                    7.01,
                                    50.63,
                                    7.22,
                                    50.78
                                    ]
                                ],
                                "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
                            },
                            "temporal": {
                                "interval": [
                                    [
                                    "2010-02-15T12:34:56Z",
                                    "null"
                                    ]
                                ],
                                "trs": "http://www.opengis.net/def/uom/ISO-8601/0/Gregorian",
                            }
                        },
                        "itemType": "feature",
                        "crs": [
                            "http://www.opengis.net/def/crs/EPSG/0/25832",
                            "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                        ],
                        "storageCrs": "http://www.opengis.net/def/crs/EPSG/0/25832",
                        "storageCrsCoordinateEpoch": 0,
                        "links": [
                            {
                                "href": "http://data.example.org/collections/buildings/items",
                                "rel": "items",
                                "type": "application/geo+json",
                                "title": "Buildings"
                            },
                            {
                                "href": "http://data.example.org/collections/buildings/items.html",
                                "rel": "items",
                                "type": "text/html",
                                "title": "Buildings"
                            },
                            {
                                "href": "https://creativecommons.org/publicdomain/zero/1.0/",
                                "rel": "license",
                                "type": "text/html",
                                "title": "CC0-1.0"
                            },
                            {
                                "href": "https://creativecommons.org/publicdomain/zero/1.0/rdf",
                                "rel": "license",
                                "type": "application/rdf+xml",
                                "title": "CC0-1.0"
                            }
                        ]
                    }
                },
                "text/html": {
                    "description": "HTML representation of the feature collection with id `collectionId`.",
                    "example": "string",
                }
            },
            "description": "Information about the feature collection with id `collectionId`.\n\nThe response contains a link to the items in the collection (path `/collections/{collectionId}/items`, link relation `items`) as well as key information about the collection. This information includes:\n\n* A local identifier for the collection that is unique for the dataset;\n\n* A list of coordinate reference systems (CRS) in which geometries may be returned by the server. The first CRS is the default coordinate reference system (the default is always WGS 84 with axis order longitude/latitude);\n\n* An optional title and description for the collection;\n\n* An optional extent that can be used to provide an indication of the spatial and temporal extent of the collection - typically derived from the data;\n\n* An optional indicator about the type of the items in the collection (the default value, if the indicator is not provided, is 'feature').",
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
    tags=["Capabilities"],
    summary="describe the feature collection with id `collectionId`",
    response_model_by_alias=True,
)
async def describe_collection(
    collectionId: Annotated[StrictStr, Field(description="local identifier of a collection")] = Path(..., description="local identifier of a collection"),
    request: Request = None,
    session = Depends(Database.get_sqlite_session),
    format: ogc_api_config.ReturnFormat = Depends(ogc_api_config.params.get_format_query)
) -> Collection:
    if not BaseCapabilitiesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseCapabilitiesApi.subclasses[0]().describe_collection(collectionId, request, format, session)


@router.get(
    "/collections",
    responses={
        200: {
            "model": Collections,
            "content": {
                "application/json": {
                    "description": "JSON representation of the feature collections.",
                    "example": {
                        "links": [
                            {
                                "href": "http://data.example.org/collections.json",
                                "rel": "self",
                                "type": "application/json",
                                "title": "this document"
                            },
                            {
                                "href": "http://data.example.org/collections.html",
                                "rel": "alternate",
                                "type": "text/html",
                                "title": "this document as HTML"
                            },
                            {
                                "href": "http://schemas.example.org/1.0/buildings.xsd",
                                "rel": "describedby",
                                "type": "application/xml",
                                "title": "GML application schema for Acme Corporation building data"
                            },
                            {
                                "href": "http://download.example.org/buildings.gpkg",
                                "rel": "enclosure",
                                "type": "application/geopackage+sqlite3",
                                "title": "Bulk download (GeoPackage)",
                                "length": 472546
                            }
                        ],
                        "collections": [
                            {
                                "id": "buildings",
                                "title": "Buildings",
                                "description": "Buildings in the city of Bonn.",
                                "extent": {
                                    "spatial": {
                                        "bbox": [
                                            [
                                            7.01,
                                            50.63,
                                            7.22,
                                            50.78
                                            ]
                                        ],
                                        "crs": "http://www.opengis.net/def/crs/OGC/1.3/CRS84"
                                    },
                                    "temporal": {
                                        "interval": [
                                            [
                                            "2010-02-15T12:34:56Z",
                                            "null"
                                            ]
                                        ],
                                        "trs": "http://www.opengis.net/def/uom/ISO-8601/0/Gregorian"
                                    },   
                                },
                                "itemType": "feature",
                                "crs": [
                                    "#/crs",
                                ],
                                "storageCrs": "http://www.opengis.net/def/crs/EPSG/0/25832",
                                "storageCrsCoordinateEpoch": 0,
                                "links": [
                                    {
                                        "href": "http://data.example.org/collections/buildings/items",
                                        "rel": "items",
                                        "type": "application/geo+json",
                                        "title": "Buildings"
                                    },
                                    {
                                        "href": "http://data.example.org/collections/buildings/items.html",
                                        "rel": "items",
                                        "type": "text/html",
                                        "title": "Buildings"
                                    },
                                    {
                                        "href": "https://creativecommons.org/publicdomain/zero/1.0/",
                                        "rel": "license",
                                        "type": "text/html",
                                        "title": "CC0-1.0"
                                    },
                                    {
                                        "href": "https://creativecommons.org/publicdomain/zero/1.0/rdf",
                                        "rel": "license",
                                        "type": "application/rdf+xml",
                                        "title": "CC0-1.0"
                                    }
                                ]
                            }
                        ],
                        "crs": [
                            "http://www.opengis.net/def/crs/OGC/1.3/CRS84",
                            "http://www.opengis.net/def/crs/EPSG/0/25832"  
                        ],
                    }
                },
                "text/html": {
                    "description": "HTML representation of the feature collections.",
                    "example": "string",
                },
            },
            "description": "The feature collections shared by this API.\n\nThe dataset is organized as one or more feature collections. This resource provides information about and access to the collections.\n\nThe response contains the list of collections. For each collection, a link to the items in the collection (path `/collections/{collectionId}/items`, link relation `items`) as well as key information about the collection. This information includes:\n\n* A local identifier for the collection that is unique for the dataset;\n\n* A list of coordinate reference systems (CRS) in which geometries may be returned by the server. The first CRS is the default coordinate reference system (the default is always WGS 84 with axis order longitude/latitude);\n\n* An optional title and description for the collection;\n\n* An optional extent that can be used to provide an indication of the spatial and temporal extent of the collection - typically derived from the data;\n\n* An optional indicator about the type of the items in the collection (the default value, if the indicator is not provided, is 'feature').",
        },
    },
    tags=["Capabilities"],
    summary="the feature collections in the dataset",
    response_model_by_alias=True,
)
async def get_collections(
    request: Request,
    format: ogc_api_config.ReturnFormat = Depends(ogc_api_config.params.get_format_query)
) -> Collections:
    if not BaseCapabilitiesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseCapabilitiesApi.subclasses[0]().get_collections(request, format)

@router.get(
    "/conformance",
    responses={
        200: {
            "model": ConfClasses,
            "content": {
                "application/json": {
                    "description": "JSON representation of the conformance declaration.",
                    "example": {
                        "conformsTo": [
                            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
                            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",
                            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/html",
                            "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson"
                        ]
                    },
                },
                "text/html": {
                    "description": "HTML representation of the conformance declaration.",
                    "example": "string",
                }
            },
            "description": "The URIs of all conformance classes supported by the server.\n\nTo support 'generic' clients that want to access multiple OGC API Features implementations - and not 'just' a specific API / server, the server declares the conformance classes it implements and conforms to."
        },
    },
    tags=["Capabilities"],
    summary="information about specifications that this API conforms to",
    response_model_by_alias=True,
)
async def get_conformance_declaration(
    format: ogc_api_config.ReturnFormat = Depends(ogc_api_config.params.get_format_query)
) -> ConfClasses:
    """A list of all conformance classes specified in a standard that the server conforms to."""
    if not BaseCapabilitiesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseCapabilitiesApi.subclasses[0]().get_conformance_declaration(format)


@router.get(
    "/",
    responses={
        200: {
            "model": LandingPage,
            "content": {
                "application/json": {
                    "description": "JSON representation of the landing page.",
                    "example": {
                        "title": "Buildings in Bonn",
                        "description": "Access to data about buildings in the city of Bonn via a Web API that conforms to the OGC API Features specification.",
                        "links": [
                            {
                                "href": "http://data.example.org/",
                                "rel": "self",
                                "type": "application/json",
                                "title": "this document"
                            },
                            {
                                "href": "http://data.example.org/api",
                                "rel": "service-desc",
                                "type": "application/vnd.oai.openapi+json;version=3.0",
                                "title": "the API definition"
                            },
                            {
                                "href": "http://data.example.org/api.html",
                                "rel": "service-doc",
                                "type": "text/html",
                                "title": "the API documentation"
                            },
                            {
                                "href": "http://data.example.org/conformance",
                                "rel": "conformance",
                                "type": "application/json",
                                "title": "OGC API conformance classes implemented by this server"
                            },
                            {
                                "href": "http://data.example.org/collections",
                                "rel": "data",
                                "type": "application/json",
                                "title": "Information about the feature collections"
                            }
                        ]
                    }
                },
                "text/html": {
                    "description": "HTML representation of the landing page.",
                    "example": "string",
                }
            },
            "description": "The landing page provides links to the API definition (link relations `service-desc` and `service-doc`), the Conformance declaration (path `/conformance`, link relation `conformance`), and the Feature Collections (path `/collections`, link relation `data`)."
        },
    },
    tags=["Capabilities"],
    summary="landing page",
    response_model_by_alias=True,
)
async def get_landing_page(
    request: Request,
    format: ogc_api_config.ReturnFormat = Depends(ogc_api_config.params.get_format_query)
) -> LandingPage:
    """The landing page provides links to the API definition, the conformance statements and to the feature collections in this dataset."""
    if not BaseCapabilitiesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseCapabilitiesApi.subclasses[0]().get_landing_page(request, format)

@router.get(
    "/api",
    responses={
        200: {
            "model": None,
            "content": {
                "application/vnd.oai.openapi+json;version=3.0": {
                    "description": "The OpenAPI schema as JSON.",
                    "example": "string",
                },
                "text/html": {
                    "description": "The OpenAPI schema as HTML.",
                    "example": "string",
                },
            },
            "description": "Get the OpenAPI schema",
        },
    },
    tags=["Capabilities"],
    summary="API definition",
    response_class=Response
)
async def get_openapi_schema(
    request: Request,
):
    """Get the OpenAPI schema in JSON or HTML format."""
    
    accept_header = request.headers.get("accept", "application/vnd.oai.openapi+json;version=3.0")
    format = request.query_params.get("f")
    app = request.app
    
    # Get the OpenAPI schema
    openapi_schema = app.openapi()
    
    if ("text/html" in accept_header and format is None) or format == "html":
        # Serve Swagger UI
        from fastapi.openapi.docs import get_swagger_ui_html
        html = get_swagger_ui_html(
            openapi_url=request.url.path + "?f=json",  # This will be requested with JSON Accept header
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=None,
            init_oauth=None,
        )
        
        return html
    else:
        # Serve OpenAPI schema as JSON
        return ORJSONResponse(content=openapi_schema, media_type="application/vnd.oai.openapi+json;version=3.0")