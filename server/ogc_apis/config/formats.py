import mimetypes
from enum import Enum


class ReturnFormat(str, Enum):
    json = "json"
    html = "html"
    
    @classmethod
    def get_default(cls):
        return cls.json
    
    @classmethod
    def get_custom_mimetypes(cls):
        return [
            {
                "ext": "geojson",
                "type": "application/geo+json",
            },
        ]

mimetypes.init()

for mimetype in ReturnFormat.get_custom_mimetypes():
    mimetypes.add_type(type=mimetype["type"], ext="." + mimetype["ext"])