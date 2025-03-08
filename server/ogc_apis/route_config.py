from enum import Enum
from fastapi.templating import Jinja2Templates
import jinja2
from pydantic import Field
from typing_extensions import Annotated

from fastapi import Query

API_ROUTE = "/api"
FEATURES_ROUTE = "/features"
TEMPLATE_RESPONSE = Jinja2Templates(directory="./../jinja_templates")
TEMPLATE_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.PackageLoader("server", "jinja_templates"),
    autoescape=jinja2.select_autoescape(),
)

class _ReturnFormat(str, Enum):
    json = "json"
    html = "html"

def get_format_query(f: _ReturnFormat = Query(default=_ReturnFormat.json, description="Optional parameter which indicates the output format of the response")) -> None:
    pass