import mimetypes
from enum import Enum
from typing import Any

from fastapi import Response
import orjson

_CUSTOM_MIMETYPES = {
    "geojson": {
        "type": "application/geo+json",
        "name": "GeoJSON"
    },
}

class GeoJSONResponse(Response):
    media_type = _CUSTOM_MIMETYPES["geojson"]["type"]
    
    def render(self, content: Any) -> bytes:
        if type(content) is dict:
            return orjson.dumps(content)
        if type(content) is str:
            return content.encode("utf-8")
        raise ValueError("Invalid content type. Expected a dictionary or string.")

class ReturnFormat(str, Enum):
    json = "json"
    html = "html"
    
    @classmethod
    def get_default(cls):
        return cls.json.name
    
    @classmethod
    def get_custon_mimetypes(cls):
        return _CUSTOM_MIMETYPES
    
    @classmethod
    def get_all(cls):
        formats = [_format.value for _format in cls]
        formats.insert(0, cls.get_default())
        return list(set(formats))

mimetypes.init()

for ext, mime_type in _CUSTOM_MIMETYPES.items():
    mimetypes.add_type(type=mime_type["type"], ext="." + ext)