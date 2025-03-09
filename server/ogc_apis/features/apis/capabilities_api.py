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
                },
                "text/html": {
                    "description": "HTML representation of the feature collection with id `collectionId`.",
                    "example": "string",
                }
            },
            "description": "Information about the feature collection with id `collectionId`.\n\nThe response contains a link to the items in the collection (path `/collections/{collectionId}/items`, link relation `items`) as well as key information about the collection. This information includes:\n\n* A local identifier for the collection that is unique for the dataset;\n\n* A list of coordinate reference systems (CRS) in which geometries may be returned by the server. The first CRS is the default coordinate reference system (the default is always WGS 84 with axis order longitude/latitude);\n\n* An optional title and description for the collection;\n\n* An optional extent that can be used to provide an indication of the spatial and temporal extent of the collection - typically derived from the data;\n\n* An optional indicator about the type of the items in the collection (the default value, if the indicator is not provided, is 'feature').",
        },
        404: {"description": "The requested resource does not exist on the server. For example, a path parameter had an incorrect value."},
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
        200: {"model": Collections, "description": "The feature collections shared by this API.\n\nThe dataset is organized as one or more feature collections. This resource provides information about and access to the collections.\n\nThe response contains the list of collections. For each collection, a link to the items in the collection (path `/collections/{collectionId}/items`, link relation `items`) as well as key information about the collection. This information includes:\n\n* A local identifier for the collection that is unique for the dataset;\n\n* A list of coordinate reference systems (CRS) in which geometries may be returned by the server. The first CRS is the default coordinate reference system (the default is always WGS 84 with axis order longitude/latitude);\n\n* An optional title and description for the collection;\n\n* An optional extent that can be used to provide an indication of the spatial and temporal extent of the collection - typically derived from the data;\n\n* An optional indicator about the type of the items in the collection (the default value, if the indicator is not provided, is 'feature')."},
    },
    tags=["Capabilities"],
    summary="the feature collections in the dataset",
    response_model_by_alias=True,
)
async def get_collections(
) -> Collections:
    if not BaseCapabilitiesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseCapabilitiesApi.subclasses[0]().get_collections()

# FIXME: Fix the response model for the conformance declaration and landing page for HTML and so on
@router.get(
    "/conformance",
    responses={
        200: {"model": ConfClasses, "description": "The URIs of all conformance classes supported by the server.\n\nTo support 'generic' clients that want to access multiple OGC API Features implementations - and not 'just' a specific API / server, the server declares the conformance classes it implements and conforms to."},
    },
    tags=["Capabilities"],
    summary="information about specifications that this API conforms to",
    response_model_by_alias=True,
    # Using ORJSONResponse as response_class to directly return the dict of the JSON string of the ConfClass object
    # Faster than returning the LandingPage object that gets serialized to a JSON string
    response_class=ORJSONResponse,
)
async def get_conformance_declaration(
) -> ConfClasses:
    """A list of all conformance classes specified in a standard that the server conforms to."""
    if not BaseCapabilitiesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    
    conformance_declaration: dict = await BaseCapabilitiesApi.subclasses[0]().get_conformance_declaration()
    
    # Using orjson.loads to convert the JSON string to a dict, up to 2x faster than json.loads
    return ORJSONResponse(content=conformance_declaration)


@router.get(
    "/",
    responses={
        200: {
            "model": LandingPage,
            "content": {
                "application/json": {
                    "description": "JSON representation of the landing page.",
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
                "application/json": {
                    "description": "The OpenAPI schema as JSON.",
                },
                "text/html": {
                    "description": "The OpenAPI schema as HTML.",
                },
            },
            "description": "Get the OpenAPI schema",
        },
    },
    tags=["Capabilities"],
    summary="API definition",
)
async def get_openapi_schema(
    request: Request,
):
    """Get the OpenAPI schema in JSON or HTML format."""
    
    accept_header = request.headers.get("accept", "application/json")
    format = request.query_params.get("f")
    app = request.app
    
    # Get the OpenAPI schema
    openapi_schema = app.openapi()
    
    if ("text/html" in accept_header and format is None) or format == "html":
        # Serve Swagger UI
        from fastapi.openapi.docs import get_swagger_ui_html
        html = get_swagger_ui_html(
            openapi_url=str(request.url.remove_query_params("f")) + "?f=json",  # This will be requested with JSON Accept header
            title=app.title + " - Swagger UI",
            oauth2_redirect_url=None,
            init_oauth=None,
        )
        
        return html
    else:
        # Serve OpenAPI schema as JSON
        return ORJSONResponse(content=openapi_schema)