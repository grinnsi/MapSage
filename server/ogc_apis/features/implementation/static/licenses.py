from server.database.models import License
from server.ogc_apis.features.implementation.static.pre_render import generate_link


def get_default_licenses() -> list[License]:
    default_licenses = [
        {
           "url": "https://creativecommons.org/publicdomain/zero/1.0/",
            "type": "text/html",
            "alternative_url": "https://creativecommons.org/publicdomain/zero/1.0/rdf",
            "alternative_type": "application/rdf+xml",
            "title": "CC0-1.0",
        },
        {
            "url": "https://creativecommons.org/licenses/by/4.0/",
            "type": "text/html",
            "alternative_url": "https://creativecommons.org/licenses/by/4.0/rdf",
            "alternative_type": "application/rdf+xml",
            "title": "CC-BY-4.0",
        },
        {
            "url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "type": "text/html",
            "alternative_url": "https://creativecommons.org/licenses/by-sa/4.0/rdf",
            "alternative_type": "application/rdf+xml",
            "title": "CC-BY-SA-4.0",
        },
        {
            "url": "https://creativecommons.org/licenses/by-nc/4.0/",
            "type": "text/html",
            "alternative_url": "https://creativecommons.org/licenses/by-nc/4.0/rdf",
            "alternative_type": "application/rdf+xml",
            "title": "CC-BY-NC-4.0",
        },
        {
            "url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
            "type": "text/html",
            "alternative_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/rdf",
            "alternative_type": "application/rdf+xml",
            "title": "CC-BY-NC-SA-4.0",
        },
        {
            "url": "https://creativecommons.org/licenses/by-nd/4.0/",
            "type": "text/html",
            "alternative_url": "https://creativecommons.org/licenses/by-nd/4.0/rdf",
            "alternative_type": "application/rdf+xml",
            "title": "CC-BY-ND-4.0",
        },
        {
            "url": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
            "type": "text/html",
            "alternative_url": "https://creativecommons.org/licenses/by-nc-nd/4.0/rdf",
            "alternative_type": "application/rdf+xml",
            "title": "CC-BY-NC-ND-4.0",
        }
    ]
    
    licenses = [License(**license) for license in default_licenses]
    
    for license in licenses:
        dict = {
            "url" : license.url,
            "type" : license.type,
            "title" : license.title,
            "rel": "license"
        }
        dict_alt = {
            "url" : license.alternative_url,
            "type" : license.alternative_type,
            "title" : license.title,
            "rel": "license"
        }
        
        license.pre_rendered_json = generate_link(dict)
        license.pre_rendered_json_alternate = generate_link(dict_alt)
    
    return licenses