import mimetypes
from server.ogc_apis import ogc_api_config

def _get_key_values(obj: dict) -> tuple[str, str, str, str]:
    href = obj.get('url', None)
    if href is None:
        href = obj.get('href', None)
        if href is None:
            raise KeyError("Object must have a 'url' or 'href' key")
    
    rel = obj.get('rel', None)
    if rel is None:
        raise KeyError("Object must have a 'rel' key")
    
    doc_type = obj.get('type', None)
    if doc_type is None:
        raise KeyError("Object must have a 'type' key")
        
    title = obj.get('title', None)
    if title is None:
        raise KeyError("Object must have a 'title' key")
    
    return href, rel, doc_type, title

def generate_link(obj: dict) -> dict:
    if not isinstance(obj, dict):
        raise TypeError("Object must be a dictionary")
    
    href, rel, doc_type, title = _get_key_values(obj)
    
    return {
        "href": href,
        "rel": rel,
        "type": doc_type,
        "title": title
    }
    
def generate_multiple_link_types(
    obj: dict, 
    formats: list[str] = ogc_api_config.ReturnFormat.get_all(), 
) -> list[dict]:
    if not isinstance(obj, dict):
        raise TypeError("Object must be a dictionary")
    
    links = []
    
    if "type" not in obj:
        obj["type"] = ""
    
    href, rel, _, title = _get_key_values(obj)
    connect_char = "&" if "?" in href else "?"
    
    custom_formats = ogc_api_config.formats.ReturnFormat.get_custon_mimetypes()
    
    for _format in formats:
        _format_name = custom_formats[_format]["name"] if _format in custom_formats else _format.upper()
        mime_type = mimetypes.types_map["." + _format]
        param_f = mime_type.split("+")[1] if "+" in mime_type else _format
        
        if "self" in rel and _format != ogc_api_config.ReturnFormat.get_default():
            rel = "alternate"
        
        links.append({
            "href": f"{href}{connect_char}f={param_f}",
            "rel": rel,
            "type": mime_type,
            "title": title.format(format_name=_format_name)
        })
    
    return links
    
def generate_links(obj: list[dict], multiple_types: bool = False, formats: list[str] = ogc_api_config.ReturnFormat.get_all()) -> list[dict]:
    if not isinstance(obj, list):
        raise TypeError("Input must be a list of dictionaries")
    
    if multiple_types:
        return [x for item in obj for x in generate_multiple_link_types(item, formats)]
    
    return [generate_link(item) for item in obj]