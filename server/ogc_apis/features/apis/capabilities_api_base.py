# coding: utf-8

from typing import ClassVar, Dict, List, Tuple  # noqa: F401

from pydantic import Field, StrictStr
from typing import Any
from typing_extensions import Annotated
from server.ogc_apis.features.models.collection import Collection
from server.ogc_apis.features.models.collections import Collections
from server.ogc_apis.features.models.conf_classes import ConfClasses
from server.ogc_apis.features.models.exception import Exception
from server.ogc_apis.features.models.landing_page import LandingPage


class BaseCapabilitiesApi:
    subclasses: ClassVar[Tuple] = ()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        BaseCapabilitiesApi.subclasses = BaseCapabilitiesApi.subclasses + (cls,)
    async def describe_collection(
        self,
        collectionId: Annotated[StrictStr, Field(description="local identifier of a collection")],
    ) -> Collection:
        ...


    async def get_collections(
        self,
    ) -> Collections:
        ...


    async def get_conformance_declaration(
        self,
    ) -> ConfClasses:
        """A list of all conformance classes specified in a standard that the server conforms to."""
        ...


    async def get_landing_page(
        self,
    ) -> LandingPage:
        """The landing page provides links to the API definition, the conformance statements and to the feature collections in this dataset."""
        ...
