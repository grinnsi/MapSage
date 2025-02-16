from typing import Collection, Union
from pydantic import Field, StrictStr
from typing_extensions import Annotated
from fastapi import Request
from server.database.db import Database
from server.database.models import PreRenderedJson
from server.ogc_apis.features.apis.capabilities_api_base import BaseCapabilitiesApi
from server.ogc_apis.features.implementation.pre_render.landing_page import generate_landing_page
from server.ogc_apis.features.models.collections import Collections
from server.ogc_apis.features.models.conf_classes import ConfClasses
from server.ogc_apis.features.models.landing_page import LandingPage


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
        request: Request
    ) -> str:
        """Return the landing page for the API."""
        pre_rendered_landing_page: Union[PreRenderedJson, list] = Database.select_sqlite_db(table_model=PreRenderedJson, primary_key_value="landing_page")
        if not isinstance(pre_rendered_landing_page, list):
            # Returns the JSON string representation of the LandingPage object
            return pre_rendered_landing_page.value
        else:
            generated_landing_page = generate_landing_page(base_url=str(request.base_url), root_path=request.scope.get("root_path", ""))
            pre_rendered_json = PreRenderedJson(key="landing_page", value=generated_landing_page.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True))
            Database.insert_sqlite_db(data_object=pre_rendered_json)

            # Returns the JSON string representation of the LandingPage object
            # This is because the response of the endpoint is ORJSONResponse which requires a dict
            # However this will return a JSON string so it's in line with the pre_rendered_json.value in the IF-statement above
            return generated_landing_page.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True)