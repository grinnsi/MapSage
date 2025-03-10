
from server.database.db import Database
from server.database.models import CollectionTable
from server.ogc_apis.features.implementation import pre_render_helper
from server.ogc_apis.features.models.collections import Collections


def generate_collections_object(collections_url: str) -> Collections:
    link_self = {
        "url": collections_url,
        "rel": "self",
        "title": "This document as {format_name}",
    }
    
    links = pre_render_helper.generate_links([link_self], multiple_types=True)
    
    all_collections: list[CollectionTable] = Database.select_sqlite_db(CollectionTable, select_all=True)
    if len(all_collections) == 0:
        return Collections(links=links, collections=[])
    
    # FIXME: Remove global crs from collections and replace with #/crs
    shared_crs = set.intersection(*map(set, [collection.crs_json for collection in all_collections]))
    all_collections_model = [collection.to_collection() for collection in all_collections]
    
    return Collections(links=links, collections=all_collections_model, crs=list(shared_crs))