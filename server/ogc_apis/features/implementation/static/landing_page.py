from server.ogc_apis import ogc_api_config

from server.database.db import Database
from server.database.models import GeneralOption
from server.ogc_apis.features.models.landing_page import LandingPage
from server.ogc_apis.features.models.link import Link
from server.ogc_apis.features.implementation import pre_render_helper


def generate_object(base_url: str) -> LandingPage:   
    title: GeneralOption = Database.select_sqlite_db(table_model=GeneralOption, primary_key_value="service_title")
    description: GeneralOption = Database.select_sqlite_db(table_model=GeneralOption, primary_key_value="service_description")
    
    domain = base_url.rstrip("/")
    features_base_route = f"{domain}{ogc_api_config.routes.FEATURES}"
    
    link_self = {
        "url": features_base_route + "/",
        "rel": "self",
        "title": "This document as {format_name}",
    }
    
    link_conformance = {
        "url": f"{features_base_route}/conformance",
        "rel": "conformance",
        "title": "OGC API conformance classes implemented by this server as {format_name}",
    }
    
    link_collections = {
        "url": f"{features_base_route}/collections",
        "rel": "data",
        "title": "Information about the feature collections as {format_name}",
    }
    
    links = pre_render_helper.generate_links([link_self, link_conformance, link_collections], multiple_types=True)
    
    links.append({
        "href": f"{features_base_route}{ogc_api_config.routes.API}",
        "rel": "service-desc",
        "type": "application/vnd.oai.openapi+json;version=3.0",
        "title": "The API definition",
    })
    
    links.append({
        "href": f"{features_base_route}{ogc_api_config.routes.API}?f=html",
        "rel": "service-doc",
        "type": "text/html",
        "title": "The API documentation",
    })
    
    landing_page = LandingPage(title=title.value, description=description.value, links=links)
    
    return landing_page