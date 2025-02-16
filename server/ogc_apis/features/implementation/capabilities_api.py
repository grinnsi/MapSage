from typing import Collection
from pydantic import Field, StrictStr
from typing_extensions import Annotated
from server.ogc_apis.features.apis.capabilities_api_base import BaseCapabilitiesApi
from server.ogc_apis.features.models.collections import Collections
from server.ogc_apis.features.models.conf_classes import ConfClasses


class CapabilitiesApi(BaseCapabilitiesApi):

    async def describe_collection(
        self,
        collectionId: Annotated[StrictStr, Field(description="local identifier of a collection")],
    ) -> Collection:
        """Return information about the feature collection with id `collectionId`."""
        raise NotImplementedError

    async def get_collections(
        self,
    ) -> Collections:
        """Return the feature collections shared by this API."""
        raise NotImplementedError

    async def get_conformance_declaration(
        self,
    ) -> ConfClasses:
        """Return information about specifications that this API conforms to."""
        raise NotImplementedError

    async def get_landing_page(
        self,
    ) -> str:
        """Return the landing page for the API."""
        raise NotImplementedError