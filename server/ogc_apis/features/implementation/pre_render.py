import orjson

def generate_link(obj: dict) -> str:
    if not isinstance(obj, dict):
        raise ValueError("Object must be a dictionary")
    
    return orjson.dumps({
        "href": obj['url'],
        "rel": obj['rel'],
        "type": obj['type'],
        "title": obj['title']
    }).decode("utf-8")
    
def generate_links(obj: list[dict]) -> str:
    if not isinstance(obj, list):
        raise ValueError("Input must be a list of dictionaries")
    
    return orjson.dumps([orjson.loads(generate_link(item)) for item in obj]).decode("utf-8")