from enum import Enum


class ReturnFormat(str, Enum):
    json = "json"
    html = "html"
    
    @classmethod
    def get_default(cls):
        return cls.json