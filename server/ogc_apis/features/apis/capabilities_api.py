# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil

from server.ogc_apis.features.apis.capabilities_api_base import BaseCapabilitiesApi
import server.ogc_apis.features.implementation as implementation

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
        200: {"model": Collection, "description": "Information about the feature collection with id &#x60;collectionId&#x60;.  The response contains a link to the items in the collection (path &#x60;/collections/{collectionId}/items&#x60;, link relation &#x60;items&#x60;) as well as key information about the collection. This information includes:  * A local identifier for the collection that is unique for the dataset; * A list of coordinate reference systems (CRS) in which geometries may be returned by the server. The first CRS is the default coordinate reference system (the default is always WGS 84 with axis order longitude/latitude); * An optional title and description for the collection; * An optional extent that can be used to provide an indication of the spatial and temporal extent of the collection - typically derived from the data; * An optional indicator about the type of the items in the collection (the default value, if the indicator is not provided, is &#39;feature&#39;)."},
        404: {"description": "The requested resource does not exist on the server. For example, a path parameter had an incorrect value."},
        500: {"model": Exception, "description": "A server error occurred."},
    },
    tags=["Capabilities"],
    summary="describe the feature collection with id &#x60;collectionId&#x60;",
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
        200: {"model": Collections, "description": "The feature collections shared by this API.  The dataset is organized as one or more feature collections. This resource provides information about and access to the collections.  The response contains the list of collections. For each collection, a link to the items in the collection (path &#x60;/collections/{collectionId}/items&#x60;, link relation &#x60;items&#x60;) as well as key information about the collection. This information includes:  * A local identifier for the collection that is unique for the dataset; * A list of coordinate reference systems (CRS) in which geometries may be returned by the server. The first CRS is the default coordinate reference system (the default is always WGS 84 with axis order longitude/latitude); * An optional title and description for the collection; * An optional extent that can be used to provide an indication of the spatial and temporal extent of the collection - typically derived from the data; * An optional indicator about the type of the items in the collection (the default value, if the indicator is not provided, is &#39;feature&#39;)."},
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
        200: {"model": ConfClasses, "description": "The URIs of all conformance classes supported by the server.  To support \&quot;generic\&quot; clients that want to access multiple OGC API Features implementations - and not \&quot;just\&quot; a specific API / server, the server declares the conformance classes it implements and conforms to."},
        500: {"model": Exception, "description": "A server error occurred."},
    },
    tags=["Capabilities"],
    summary="information about specifications that this API conforms to",
    response_model_by_alias=True,
)
async def get_conformance_declaration(
) -> ConfClasses:
    """A list of all conformance classes specified in a standard that the server conforms to."""
    if not BaseCapabilitiesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseCapabilitiesApi.subclasses[0]().get_conformance_declaration()


@router.get(
    "/",
    responses={
        200: {"model": LandingPage, "description": "The landing page provides links to the API definition (link relations &#x60;service-desc&#x60; and &#x60;service-doc&#x60;), the Conformance declaration (path &#x60;/conformance&#x60;, link relation &#x60;conformance&#x60;), and the Feature Collections (path &#x60;/collections&#x60;, link relation &#x60;data&#x60;)."},
        500: {"model": Exception, "description": "A server error occurred."},
    },
    tags=["Capabilities"],
    summary="landing page",
    response_model_by_alias=True,
)
async def get_landing_page(
) -> LandingPage:
    """The landing page provides links to the API definition, the conformance statements and to the feature collections in this dataset."""
    if not BaseCapabilitiesApi.subclasses:
        raise HTTPException(status_code=500, detail="Not implemented")
    return await BaseCapabilitiesApi.subclasses[0]().get_landing_page()
