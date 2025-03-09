from enum import Enum
from fastapi.templating import Jinja2Templates
import jinja2
from pydantic import Field
from typing_extensions import Annotated

from fastapi import Query

TEMPLATE_RESPONSE = Jinja2Templates(directory="./../jinja_templates")
TEMPLATE_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.PackageLoader("server", "jinja_templates"),
    autoescape=jinja2.select_autoescape(),
)

def get_template(name: str) -> Jinja2Templates:
    try:
        return TEMPLATE_ENVIRONMENT.get_template(name)
    except jinja2.exceptions.TemplateNotFound:
        raise ValueError(f"Template {name} not found")

API_ROUTE = "/api"
FEATURES_ROUTE = "/features"

class ReturnFormat(str, Enum):
    json = "json"
    html = "html"

def get_format_query(f: Annotated[ReturnFormat, Field(default=ReturnFormat.json, description="Optional parameter which indicates the output format of the response")] = Query(default=ReturnFormat.json, description="Optional parameter which indicates the output format of the response")) -> None:
    return f