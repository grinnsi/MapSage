# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from fastapi.responses import ORJSONResponse
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
from server.ogc_apis.features.models.exception import Exception
from server.ogc_apis.features.models.landing_page import LandingPage


router = APIRouter()

ns_pkg = implementation
for _, name, _ in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


@router.get(
    "/collections/{collectionId}",
    responses={
        200: {"model": Collection, "description": "Information about the feature collection with id `collectionId`.\n\nThe response contains a link to the items in the collection (path `/collections/{collectionId}/items`, link relation `items`) as well as key information about the collection. This information includes:\n\n* A local identifier for the collection that is unique for the dataset;\n\n* A list of coordinate reference systems (CRS) in which geometries may be returned by the server. The first CRS is the default coordinate reference system (the default is always WGS 84 with axis order longitude/latitude);\n\n* An optional title and description for the collection;\n\n* An optional extent that can be used to provide an indication of the spatial and temporal extent of the collection - typically derived from the data;\n\n* An optional indicator about the type of the items in the collection (the default value, if the indicator is not provided, is 'feature')."},
        404: {"description": "The requested resource does not exist on the server. For example, a path parameter had an incorrect value."},
        500: {"model": Exception, "description": "A server error occurred."},
    },
    tags=["Capabilities"],
    summary="describe the feature collection with id `collectionId`",
    response_model_by_alias=True,
)
async def describe_collection(
    collectionId: Annotated[StrictStr, Field(description="local identifier of a collection")] = Path(..., description="local identifier of a collection"),
) -> Collection:
    if not BaseCapabilitiesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseCapabilitiesApi.subclasses[0]().describe_collection(collectionId)


@router.get(
    "/collections",
    responses={
        200: {"model": Collections, "description": "The feature collections shared by this API.\n\nThe dataset is organized as one or more feature collections. This resource provides information about and access to the collections.\n\nThe response contains the list of collections. For each collection, a link to the items in the collection (path `/collections/{collectionId}/items`, link relation `items`) as well as key information about the collection. This information includes:\n\n* A local identifier for the collection that is unique for the dataset;\n\n* A list of coordinate reference systems (CRS) in which geometries may be returned by the server. The first CRS is the default coordinate reference system (the default is always WGS 84 with axis order longitude/latitude);\n\n* An optional title and description for the collection;\n\n* An optional extent that can be used to provide an indication of the spatial and temporal extent of the collection - typically derived from the data;\n\n* An optional indicator about the type of the items in the collection (the default value, if the indicator is not provided, is 'feature')."},
        500: {"model": Exception, "description": "A server error occurred."},
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


@router.get(
    "/conformance",
    responses={
        200: {"model": ConfClasses, "description": "The URIs of all conformance classes supported by the server.\n\nTo support 'generic' clients that want to access multiple OGC API Features implementations - and not 'just' a specific API / server, the server declares the conformance classes it implements and conforms to."},
        500: {"model": Exception, "description": "A server error occurred."},
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
        200: {"model": LandingPage, "description": "The landing page provides links to the API definition (link relations `service-desc` and `service-doc`), the Conformance declaration (path `/conformance`, link relation `conformance`), and the Feature Collections (path `/collections`, link relation `data`)."},
        500: {"model": Exception, "description": "A server error occurred."},
    },
    tags=["Capabilities"],
    summary="landing page",
    response_model_by_alias=True,
    # Using ORJSONResponse as response_class to directly return the dict of the JSON string of the LandingPage object
    # Faster than returning the LandingPage object that gets serialized to a JSON string
    response_class=ORJSONResponse,
)
async def get_landing_page(
    request: Request,
) -> LandingPage:
    """The landing page provides links to the API definition, the conformance statements and to the feature collections in this dataset."""
    if not BaseCapabilitiesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")

    landing_page: dict = await BaseCapabilitiesApi.subclasses[0]().get_landing_page(request)
    
    # Using orjson.loads to convert the JSON string to a dict, up to 2x faster than json.loads (according to author)
    return ORJSONResponse(content=landing_page)