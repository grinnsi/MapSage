import mimetypes
from enum import Enum

_CUSTOM_MIMETYPES = {
    "geojson": {
        "type": "application/geo+json",
        "name": "GeoJSON"
    },
}

class ReturnFormat(str, Enum):
    json = "json"
    html = "html"
    
    @classmethod
    def get_default(cls):
        return cls.json
    
    @classmethod
    def get_custon_mimetypes(cls):
        return _CUSTOM_MIMETYPES

mimetypes.init()

for ext, mime_type in _CUSTOM_MIMETYPES.items():
    mimetypes.add_type(type=mime_type["type"], ext="." + ext)