from typing import Collection, Union
from fastapi.responses import HTMLResponse, ORJSONResponse
from pydantic import Field, StrictStr
from typing_extensions import Annotated
from fastapi import HTTPException, Request
import sqlmodel

from server.database.db import Database
from server.database import models
from server.ogc_apis import ogc_api_config
from server.ogc_apis.features.apis.capabilities_api_base import BaseCapabilitiesApi
from server.ogc_apis.features.implementation.static.conformance import generate_conformance_declaration_object
from server.ogc_apis.features.implementation.static.landing_page import generate_landing_page_object
from server.ogc_apis.features.models.collections import Collections
from server.ogc_apis.features.models.conf_classes import ConfClasses

# TODO: Using Depends for SQLite session, so its cleanup is handled after sending of response, not during it

class CapabilitiesApi(BaseCapabilitiesApi):

    async def describe_collection(
        self,
        collectionId: Annotated[StrictStr, Field(description="local identifier of a collection")],
        request: Request,
        format: ogc_api_config.ReturnFormat,
        session: sqlmodel.Session,
    ) -> Collection:
        """Return information about the feature collection with id `collectionId`."""
        
        collections: list[models.CollectionTable] = session.exec(
            statement=sqlmodel.select(models.CollectionTable).where(models.CollectionTable.id == collectionId)
        ).all()
        if len(collections) == 0:
            raise HTTPException(status_code=404, detail="The requested resource does not exist on the server. For example, a path parameter had an incorrect value.")
        elif len(collections) > 1:
            raise HTTPException(status_code=500, detail="Multiple collections with the same id found in the database.")
        
        collection = collections[0]
        if collection.pre_rendered_json is None:
            collection.pre_render(str(request.base_url))
            Database.update_sqlite_db(data_object=collection)
        
        if format == ogc_api_config.ReturnFormat.html:
            html = ogc_api_config.templates.render("collection.html",
                collection=collection,
            )
            
            return HTMLResponse(status_code=200, content=html)

        return ORJSONResponse(content=collection.pre_rendered_json, status_code=200)

    async def get_collections(
        self,
    ) -> Collections:
        """Return the feature collections shared by this API."""
        raise NotImplementedError

    async def get_conformance_declaration(
        self,
    ) -> ConfClasses:
        """Return information about specifications that this API conforms to."""
        
        pre_rendered_conformance_declaration: Union[models.PreRenderedJson, None] = Database.select_sqlite_db(table_model=models.PreRenderedJson, primary_key_value="conformance_declaration")
        if pre_rendered_conformance_declaration:
            # Returns the JSON string representation of the ConfClasses object
            return pre_rendered_conformance_declaration.json_value
        else:
            generated_conformance_declaration = generate_conformance_declaration_object()
            pre_rendered_json = models.PreRenderedJson(key="conformance_declaration", json_value=generated_conformance_declaration.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True))
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
        
        pre_rendered_landing_page: Union[models.PreRenderedJson, None] = Database.select_sqlite_db(table_model=models.PreRenderedJson, primary_key_value="landing_page")
        if pre_rendered_landing_page:
            # Returns the JSON string representation of the LandingPage object
            return pre_rendered_landing_page.json_value
        else:
            generated_landing_page = generate_landing_page_object(base_url=str(request.base_url))
            pre_rendered_json = models.PreRenderedJson(key="landing_page", json_value=generated_landing_page.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True))
            Database.insert_sqlite_db(data_object=pre_rendered_json)

            # Returns the JSON string representation of the LandingPage object
            # This is because the response of the endpoint is ORJSONResponse which requires a dict
            # However this will return a JSON string so it's in line with the pre_rendered_json.value in the IF-statement above
            return pre_rendered_json.json_value