from typing import Optional, Self
import uuid as unique_id

from sqlalchemy import Column, ForeignKey, String
from sqlmodel import Field, Relationship, SQLModel
from sqlalchemy.orm import declared_attr
from sqlalchemy.dialects.postgresql import UUID as pg_uuid

from server.ogc_apis.features.implementation import pre_render
from server.utils.string_utils import camel_to_snake

# All custom models should inherit from CoreModel, so they have snake_case tablenames in the sqlite db
class CoreModel(SQLModel):
    @declared_attr
    def __tablename__(cls) -> str:
        # Convert CamelCase class name to snake_case table name
        name = camel_to_snake(cls.__name__)
        
        # Remove "table" from the end of the name and remove leading and trailing underscores
        name = name.replace("table", "")
        name = name.rstrip("_")
        name = name.lstrip("_")
        
        return name

class TableBase(CoreModel):
    uuid: unique_id.UUID = Field(default_factory=unique_id.uuid4, primary_key=True)

class Connection(TableBase, table=True):
    name: str
    host: str
    port: int
    role: str
    password: str
    database_name: str
    
    collections: list["CollectionTable"] = Relationship(back_populates="connection")
    
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
    
    collections: list["CollectionTable"] = Relationship(back_populates="license")
    
    @classmethod
    def get_default_licenses(cls) -> list[Self]:
        default_licenses = [
            {
            "url": "https://creativecommons.org/publicdomain/zero/1.0/",
                "type": "text/html",
                "alternative_url": "https://creativecommons.org/publicdomain/zero/1.0/rdf",
                "alternative_type": "application/rdf+xml",
                "title": "CC0-1.0",
            },
            {
                "url": "https://creativecommons.org/licenses/by/4.0/",
                "type": "text/html",
                "alternative_url": "https://creativecommons.org/licenses/by/4.0/rdf",
                "alternative_type": "application/rdf+xml",
                "title": "CC-BY-4.0",
            },
            {
                "url": "https://creativecommons.org/licenses/by-sa/4.0/",
                "type": "text/html",
                "alternative_url": "https://creativecommons.org/licenses/by-sa/4.0/rdf",
                "alternative_type": "application/rdf+xml",
                "title": "CC-BY-SA-4.0",
            },
            {
                "url": "https://creativecommons.org/licenses/by-nc/4.0/",
                "type": "text/html",
                "alternative_url": "https://creativecommons.org/licenses/by-nc/4.0/rdf",
                "alternative_type": "application/rdf+xml",
                "title": "CC-BY-NC-4.0",
            },
            {
                "url": "https://creativecommons.org/licenses/by-nc-sa/4.0/",
                "type": "text/html",
                "alternative_url": "https://creativecommons.org/licenses/by-nc-sa/4.0/rdf",
                "alternative_type": "application/rdf+xml",
                "title": "CC-BY-NC-SA-4.0",
            },
            {
                "url": "https://creativecommons.org/licenses/by-nd/4.0/",
                "type": "text/html",
                "alternative_url": "https://creativecommons.org/licenses/by-nd/4.0/rdf",
                "alternative_type": "application/rdf+xml",
                "title": "CC-BY-ND-4.0",
            },
            {
                "url": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
                "type": "text/html",
                "alternative_url": "https://creativecommons.org/licenses/by-nc-nd/4.0/rdf",
                "alternative_type": "application/rdf+xml",
                "title": "CC-BY-NC-ND-4.0",
            }
        ]
        
        licenses = [License(**license) for license in default_licenses]
        
        for license in licenses:
            dict = {
                "url" : license.url,
                "type" : license.type,
                "title" : license.title,
                "rel": "license"
            }
            dict_alt = {
                "url" : license.alternative_url,
                "type" : license.alternative_type,
                "title" : license.title,
                "rel": "license"
            }
            
            license.pre_rendered_json = pre_render.generate_link(dict)
            license.pre_rendered_json_alternate = pre_render.generate_link(dict_alt)
            
        return licenses
    
class CollectionTable(TableBase, table=True):
    # id with index for faster search when querying specific id
    id: str = Field(index=True, unique=True)
    layer_name: str
    title: str
    description: str = Field(default="")
    links_json: str                                                                                         # JSON
    
    license_title: Optional[str] = Field(default=None, sa_column=Column(String, ForeignKey(f"{License.__tablename__}.title", ondelete="SET NULL", onupdate="CASCADE"), nullable=True))
    
    bbox_json: Optional[str] = Field(default=None)                                                          # JSON
    bbox_crs: Optional[str] = Field(default=None)
    interval_json: Optional[str] = Field(default=None)                                                      # JSON

    crs_json: str = Field(default="""["http://www.opengis.net/def/crs/OGC/1.3/CRS84"]""")                   # JSON
    storage_crs: str = Field(default="http://www.opengis.net/def/crs/OGC/1.3/CRS84")
    storage_crs_coordinate_epoch: Optional[float] = Field(default=None)
    
    connection_uuid: unique_id.UUID = Field(sa_column=Column(pg_uuid(as_uuid=True), ForeignKey(f"{Connection.__tablename__}.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False))
    
    pre_rendered_json: Optional[str] = Field(default=None)                                             # JSON
    
    license: Optional[License] = Relationship(back_populates="collections")
    connection: Connection = Relationship(back_populates="collections")

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