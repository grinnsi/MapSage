import re
import orjson
import server.ogc_apis.route_config as route_config

_link_attributes_regex = re.compile(r"(href|rel|type|title)\"[\s\n]*:[\s\n]*\"([^\"]*)")

def generate_link(obj: dict) -> dict:
    if not isinstance(obj, dict):
        raise ValueError("Object must be a dictionary")
    
    href = obj.get('url', None)
    if href is None:
        href = obj.get('href', None)
    if href is None:
        raise ValueError("Object must have a 'url' or 'href' key")
    
    rel = obj.get('rel', None)
    if rel is None:
        raise ValueError("Object must have a 'rel' key")
    
    doc_type = obj.get('type', None)
    if doc_type is None:
        raise ValueError("Object must have a 'type' key")
        
    title = obj.get('title', None)
    if title is None:
        raise ValueError("Object must have a 'title' key")
    
    return {
        "href": href,
        "rel": rel,
        "type": doc_type,
        "title": title
    }
    
def generate_links(obj: list[dict]) -> list[dict]:
    if not isinstance(obj, list):
        raise ValueError("Input must be a list of dictionaries")
    
    return [generate_link(item) for item in obj]

def generate_basic_html_from_json(title: str, description: str, json: str) -> str:
    if not isinstance(json, str):
        raise ValueError("Input must be a JSON string")
    
    # Format JSON to be more readable
    obj = orjson.loads(json)
    json_formated_str = orjson.dumps(obj, option=orjson.OPT_INDENT_2).decode("utf-8")
    
    links = _link_attributes_regex.findall(json_formated_str)

    template = route_config.TEMPLATE_ENVIRONMENT.get_template("json.html")
    html = template.render(
        title=title,
        description=description,
        json=json_formated_str,
    )

    return html