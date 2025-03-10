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
from server.ogc_apis.features.implementation import static
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
        request: Request,
        format: ogc_api_config.ReturnFormat,
    ) -> Collections:
        """Return the feature collections shared by this API."""
        
        pre_rendered_collections: Union[models.PreRenderedJson, None] = Database.select_sqlite_db(table_model=models.PreRenderedJson, primary_key_value="collections")
        if not pre_rendered_collections:
            collections_url = str(request.url).split("?")[0]
            generated_collections = static.generate_collections_object(collections_url=collections_url)
            pre_rendered_collections = models.PreRenderedJson(key="collections", json_value=generated_collections.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True))
            Database.insert_sqlite_db(data_object=pre_rendered_collections)
            
        if format == ogc_api_config.ReturnFormat.html:
            html = ogc_api_config.templates.RESPONSE.TemplateResponse(
                request=request,
                name="collections.html",
                context= {
                    "collections": pre_rendered_collections.json_value,
                }
            )
            return html
        
        return ORJSONResponse(content=pre_rendered_collections.json_value, status_code=200)

    async def get_conformance_declaration(
        self,
        format: ogc_api_config.ReturnFormat,
    ) -> ConfClasses:
        """Return information about specifications that this API conforms to."""
        
        pre_rendered_conformance_declaration: Union[models.PreRenderedJson, None] = Database.select_sqlite_db(table_model=models.PreRenderedJson, primary_key_value="conformance_declaration")
        if not pre_rendered_conformance_declaration:
            generated_conformance_declaration = static.generate_conformance_declaration_object()
            pre_rendered_conformance_declaration = models.PreRenderedJson(key="conformance_declaration", json_value=generated_conformance_declaration.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True))
            Database.insert_sqlite_db(data_object=pre_rendered_conformance_declaration)

        if format == ogc_api_config.ReturnFormat.html:
            html = ogc_api_config.templates.render("conformance_declaration.html",
                conf_classes=pre_rendered_conformance_declaration.json_value,
            )
            return HTMLResponse(status_code=200, content=html)
        
        return ORJSONResponse(content=pre_rendered_conformance_declaration.json_value, status_code=200)

    async def get_landing_page(
        self, 
        request: Request,
        format: ogc_api_config.ReturnFormat,
    ) -> str:
        """Return the landing page for the API."""
        
        pre_rendered_landing_page: Union[models.PreRenderedJson, None] = Database.select_sqlite_db(table_model=models.PreRenderedJson, primary_key_value="landing_page")
        if not pre_rendered_landing_page:
            generated_landing_page = static.generate_landing_page_object(base_url=str(request.base_url))
            pre_rendered_landing_page = models.PreRenderedJson(key="landing_page", json_value=generated_landing_page.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True))
            Database.insert_sqlite_db(data_object=pre_rendered_landing_page)
        
        if format == ogc_api_config.ReturnFormat.html:
            html = ogc_api_config.templates.render("landing_page.html",
                landing_page=pre_rendered_landing_page.json_value,
            )
            return HTMLResponse(status_code=200, content=html)
        
        return ORJSONResponse(content=pre_rendered_landing_page.json_value, status_code=200)