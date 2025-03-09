from server.ogc_apis import ogc_api_config

from server.database.db import Database
from server.database.models import GeneralOption
from server.ogc_apis.features.models.landing_page import LandingPage
from server.ogc_apis.features.models.link import Link


def generate_landing_page_object(base_url: str) -> LandingPage:   
    title: GeneralOption = Database.select_sqlite_db(table_model=GeneralOption, primary_key_value="service_title")
    description: GeneralOption = Database.select_sqlite_db(table_model=GeneralOption, primary_key_value="service_description")
    
    domain = base_url.rstrip("/")
    features_base_route = f"{domain}{ogc_api_config.routes.FEATURES}"
    
    known_links = [
        Link(href=features_base_route, rel="self", type="application/json", title="This document"),
        Link(href=f"{features_base_route}{ogc_api_config.routes.API}.json", rel="service-desc", type="application/vnd.oai.openapi+json;version=3.0", title="the API definition"),
        Link(href=f"{features_base_route}{ogc_api_config.routes.API}.html", rel="service-doc", type="text/html", title="the API documentation"),
        Link(href=f"{features_base_route}/conformance", rel="conformance", type="application/json", title="OGC API conformance classes implemented by this server"),
        Link(href=f"{features_base_route}/collections", rel="data", type="application/json", title="Information about the feature collections"),
    ]
    
    landing_page = LandingPage(title=title.value, description=description.value, links=known_links)
    
    return landing_page