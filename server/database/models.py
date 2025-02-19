from typing import Optional
import uuid as unique_id

from sqlmodel import Field, SQLModel
from sqlalchemy.orm import declared_attr

from server.utils.string_utils import camel_to_snake

# All custom models should inherit from CoreModel, so they have snake_case tablenames in the sqlite db
class CoreModel(SQLModel):
    @declared_attr
    def __tablename__(cls) -> str:
        return camel_to_snake(cls.__name__)

class TableBase(CoreModel):
    uuid: unique_id.UUID = Field(default_factory=unique_id.uuid4, primary_key=True)

class Connection(TableBase, table=True):
    name: str
    host: str
    port: int
    role: str
    password: str
    database_name: str
    
# class Namespace(TableBase, table=True):
#     name: str
#     url: str

class License(TableBase, table=True):
    title: str = Field(unique=True)
    url: str
    type: str = Field(default="text/html")
    alternative_url: Optional[str] = Field(default=None)
    alternative_type: Optional[str] = Field(default=None)

    pre_rendered_json: Optional[str] = Field(default=None)                                             # JSON absolut nicht schön
    pre_rendered_json_alternate: Optional[str] = Field(default=None)                                   # JSON

class KeyValueBase(CoreModel):
    key: str = Field(primary_key=True, unique=True)
    value: str

class GeneralOption(KeyValueBase, table=True):
    
    @classmethod
    def get_default_options(cls) -> dict:
        default_options = {
            "service_title": "OGC Features API",
            "service_description": "A OGC compliant Features API"
        }
        return default_options

class PreRenderedJson(KeyValueBase, table=True):
    pass