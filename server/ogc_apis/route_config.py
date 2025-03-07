from enum import Enum

from fastapi import Query

API_ROUTE = "/api"
FEATURES_ROUTE = "/features"

class _ReturnFormat(str, Enum):
    json = "json"
    html = "html"

def get_format_query(f: _ReturnFormat = Query(default=_ReturnFormat.json, description="Optional parameter which indicates the output format of the response")) -> None:
    pass