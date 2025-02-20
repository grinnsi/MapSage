import orjson

def generate_link(obj: dict | list[dict]) -> str:
    if isinstance(obj, list):
        return orjson.dumps([orjson.loads(generate_link(item)) for item in obj])
    
    return orjson.dumps({
        "href": obj['url'],
        "rel": obj['rel'],
        "type": obj['type'],
        "title": obj['title']
    })