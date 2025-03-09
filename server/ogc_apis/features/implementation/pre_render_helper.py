import re

def generate_link(obj: dict) -> dict:
    if not isinstance(obj, dict):
        raise TypeError("Object must be a dictionary")
    
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
    
    return {
        "href": href,
        "rel": rel,
        "type": doc_type,
        "title": title
    }
    
def generate_links(obj: list[dict]) -> list[dict]:
    if not isinstance(obj, list):
        raise TypeError("Input must be a list of dictionaries")
    
    return [generate_link(item) for item in obj]