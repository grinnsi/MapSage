from server.ogc_apis.features.models.conf_classes import ConfClasses

def generate_conformance_declaration() -> ConfClasses:
    conforms_to = [
        "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/core",
        "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/oas30",
        "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/html",
        "http://www.opengis.net/spec/ogcapi-features-1/1.0/conf/geojson",
        "http://www.opengis.net/spec/ogcapi-features-2/1.0/conf/crs",
    ]
    
    conf_classes = ConfClasses(conforms_to=conforms_to)
    
    return conf_classes