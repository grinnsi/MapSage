from typing import Collection, Union
from pydantic import Field, StrictStr
from typing_extensions import Annotated
from fastapi import Request
from server.database.db import Database
from server.database.models import PreRenderedJson
from server.ogc_apis.features.apis.capabilities_api_base import BaseCapabilitiesApi
from server.ogc_apis.features.implementation.static.conformance import generate_conformance_declaration_object
from server.ogc_apis.features.implementation.static.landing_page import generate_landing_page_object
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
        
        pre_rendered_conformance_declaration: Union[PreRenderedJson, None] = Database.select_sqlite_db(table_model=PreRenderedJson, primary_key_value="conformance_declaration")
        if pre_rendered_conformance_declaration:
            # Returns the JSON string representation of the ConfClasses object
            return pre_rendered_conformance_declaration.json_value
        else:
            generated_conformance_declaration = generate_conformance_declaration_object()
            pre_rendered_json = PreRenderedJson(key="conformance_declaration", json_value=generated_conformance_declaration.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True))
            Database.insert_sqlite_db(data_object=pre_rendered_json)

            # Returns the JSON string representation of the ConfClasses object
            # This is because the response of the endpoint is ORJSONResponse which requires a dict
            # However this will return a JSON string so it's in line with the pre_rendered_json.value in the IF-statement above
            return pre_rendered_json.json_value

    async def get_landing_page(
        self, 
        request: Request
    ) -> str:
        """Return the landing page for the API."""
        
        pre_rendered_landing_page: Union[PreRenderedJson, None] = Database.select_sqlite_db(table_model=PreRenderedJson, primary_key_value="landing_page")
        if pre_rendered_landing_page:
            # Returns the JSON string representation of the LandingPage object
            return pre_rendered_landing_page.json_value
        else:
            generated_landing_page = generate_landing_page_object(base_url=str(request.base_url))
            pre_rendered_json = PreRenderedJson(key="landing_page", json_value=generated_landing_page.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True))
            Database.insert_sqlite_db(data_object=pre_rendered_json)

            # Returns the JSON string representation of the LandingPage object
            # This is because the response of the endpoint is ORJSONResponse which requires a dict
            # However this will return a JSON string so it's in line with the pre_rendered_json.value in the IF-statement above
            return pre_rendered_json.json_value