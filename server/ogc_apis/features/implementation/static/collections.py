from server.database.db import Database, DatabaseSession
from server.database.models import CollectionTable, PreRenderedJson
from server.ogc_apis.features.implementation import pre_render_helper
from server.ogc_apis.features.models.collections import Collections
from server.ogc_apis import config

def generate_object(collections_url: str) -> Collections:
    link_self = {
        "url": collections_url,
        "rel": "self",
        "title": "This document as {format_name}",
    }
    
    links = pre_render_helper.generate_links([link_self], multiple_types=True)
    
    all_collections: list[CollectionTable] = Database.select_sqlite_db(CollectionTable, select_all=True)
    if len(all_collections) == 0:
        return Collections(links=links, collections=[])
    
    shared_crs = list(set.intersection(*map(set, [collection.crs_json for collection in all_collections])))
    for collection in all_collections:
        specific_crs = [crs for crs in collection.crs_json if crs not in shared_crs]
        specific_crs.insert(0, "#/crs")
        collection.crs_json = specific_crs
    
    all_collections_model = [collection.to_collection() for collection in all_collections]
    
    return Collections(links=links, collections=all_collections_model, crs=shared_crs)

def update_database_object(collections_url: str = None, app_base_url: str = None) -> PreRenderedJson:
    """
    Generates the collections model and updates or inserts it as a pre rendered object into the database.
    
    Parameters:
        collections_url (str, optional): The URL of the collections, defaults to None.
        app_base_url (str, optional): The base url of the application, defaults to None.
        
    Returns:
        PreRenderedJson: The pre-rendered object (table model) of the collections model.
    """
    
    if collections_url is None and app_base_url is None:
        raise ValueError("Either collections_url or base_url must be provided.")
    
    if collections_url is None:
        app_base_url = app_base_url.lstrip("/")
        collections_url = f"{app_base_url}{config.routes.FEATURES}/collections"
    
    with DatabaseSession() as session:
        generated_collections = generate_object(collections_url)
        pre_rendered_collections = PreRenderedJson(key="collections", json_value=generated_collections.model_dump_json(by_alias=True, exclude_unset=True, exclude_none=True))
        collections_object = session.get(PreRenderedJson, pre_rendered_collections.key)
        if collections_object:      # If the prerendered json with the key already exists
            collections_object.sqlmodel_update(pre_rendered_collections)
            session.add(collections_object)
            session.commit()
            session.refresh(collections_object)
        else:                       # If the prerendered json with the key does not exist
            session.add(pre_rendered_collections)
            session.commit()
            session.refresh(pre_rendered_collections)

    return pre_rendered_collections