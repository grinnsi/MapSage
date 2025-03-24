import enum
from typing import Any, Optional, Self
import uuid as unique_id

import orjson
from pydantic import field_validator
from sqlalchemy import Column, ForeignKey, String
from sqlmodel import Field, Relationship, SQLModel, Enum
from sqlalchemy.orm import declared_attr
from sqlalchemy.dialects.postgresql import UUID as pg_uuid
from sqlalchemy import engine

from server.ogc_apis.features.models import collection as features_api_collection
from server.ogc_apis.features.implementation import pre_render_helper
from server.utils.string_utils import camel_to_snake
from server.ogc_apis import ogc_api_config

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
    
    # Overwrite __setattr__ to automatically convert list and dict to json strings, when directly setting the attribute
    def __setattr__(self, name, value):
        if 'json' in name.lower() and value is not None and not isinstance(value, str):
            if isinstance(value, (list, dict)):
                value = orjson.dumps(value).decode("utf-8")
            else:
                raise ValueError("JSON field must be a string, list or dictionary")
        
        super().__setattr__(name, value)
    
    # Overwrite __getattribute__ to automatically convert json strings to list or dict, when accessing the attribute
    def __getattribute__(self, name):
        if 'json' in name.lower():
            value = super().__getattribute__(name)
            if value is not None:
                return orjson.loads(value)
        
        return super().__getattribute__(name)
    
    # Adding field validators for all fields containing 'json' in their name, when creating an instance of the class
    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs):
        super().__pydantic_init_subclass__(**kwargs)
        
        for field_name, _ in cls.model_fields.items():
            if 'json' in field_name:
                # Create a validator function for this specific field
                field_validator(field_name, mode="before")(cls._create_json_field_validator(field_name))
        
    @classmethod
    def _create_json_field_validator(cls, field_name):
        def validate_json_field(value: Any) -> str:            
            if value is None:
                return None
            
            if not isinstance(value, (str, dict, list)):
                raise ValueError("JSON Field must be a string, list or dictionary")
            
            if isinstance(value, str):
                return value
            
            return orjson.dumps(value).decode("utf-8")
        
        # Set a name for the validator function for better error messages
        validate_json_field.__name__ = f"validate_{field_name}"
        return validate_json_field

class TableBase(CoreModel):
    uuid: unique_id.UUID = Field(default_factory=unique_id.uuid4, primary_key=True)

class Dataset(TableBase, table=True):
    class Type(str, enum.Enum):
        DB = "db"
        SHAPE = "shape"
        GPKG = "gpkg"
        GEOJSON = "geojson"
        CSV = "csv"

    name: str
    type: Type = Field(sa_column=Column(Enum(Type)))
    # Path or connection string to the dataset
    path: str
    
    collections: list["CollectionTable"] = Relationship(back_populates="dataset", cascade_delete=True)
    
    @classmethod
    def from_dict(cls, obj: dict) -> Self:
        name = obj.get("name", None)
        if name is None:
            raise ValueError("Name is required")
        
        type_value = obj.get("type", None)
        if type_value is None:
            raise ValueError("Type is required")
        if type_value not in cls.Type:
            raise ValueError(f"Type must be one of {cls.Type.__members__.keys()}")
        
        if type_value == cls.Type.DB:
            path = engine.URL.create(
                "postgresql",
                username=obj["role"],
                password=obj["password"],
                host=obj["host"],
                port=obj["port"],
                database=obj["database_name"]
            ).__to_string__(hide_password=False)
        else:
            path = obj.get("path", None)
            if path is None:
                raise ValueError("Path is required")
        
        return cls(
            name=name,
            type=cls.Type(type_value),
            path=path
        )
    
    def to_dict(self, short: bool = False, show_password: bool = False) -> dict:
        if short:
            return {
                "uuid": self.uuid,
                "name": self.name,
                "type": self.type,
                "path": self.path
            }
            
        obj = {
            "uuid": self.uuid,
            "name": self.name,
            "type": self.type,
        }

        if self.type == self.Type.DB:
            connection_string = engine.make_url(self.path)
            obj["host"] = connection_string.host
            obj["port"] = connection_string.port
            obj["role"] = connection_string.username
            obj["password"] = connection_string.password if show_password else "********"
            obj["database_name"] = connection_string.database
        else:
            obj["path"] = self.path
            
        return obj
            
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
        
        licenses = [License().model_validate(license) for license in default_licenses]
        
        for license in licenses:
            dict_main = {
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
            
            license.pre_rendered_json = pre_render_helper.generate_link(dict_main)
            license.pre_rendered_json_alternate = pre_render_helper.generate_link(dict_alt)
            
        return licenses
    
class CollectionTable(TableBase, table=True):
    # id with index for faster search when querying specific id
    id: str = Field(index=True, unique=True)
    layer_name: str
    title: str
    description: str = Field(default="")
    links_json: str                                                                                         # JSON
    
    license_title: Optional[str] = Field(default=None, sa_column=Column(String, ForeignKey(f"{License.__tablename__}.title", ondelete="SET NULL", onupdate="CASCADE"), nullable=True))
    
    extent_json: Optional[str] = Field(default=None)                                                        # JSON
    date_time_field: Optional[str] = Field(default=None)
    # spatial_extent_crs: Optional[str] = Field(default=None)
    # temporal_extent_trs: Optional[str] = Field(default=None)
    is_3D: bool = Field(default=False)

    crs_json: str = Field(default="""["http://www.opengis.net/def/crs/OGC/1.3/CRS84"]""")                   # JSON
    storage_crs: str = Field(default="http://www.opengis.net/def/crs/OGC/1.3/CRS84")
    storage_crs_coordinate_epoch: Optional[float] = Field(default=None)
    
    dataset_uuid: unique_id.UUID = Field(sa_column=Column(pg_uuid(as_uuid=True), ForeignKey(f"{Dataset.__tablename__}.uuid", ondelete="CASCADE", onupdate="CASCADE"), nullable=False))
    
    pre_rendered_json: Optional[str] = Field(default=None)                                                  # JSON
    
    license: Optional[License] = Relationship(back_populates="collections")
    dataset: Dataset = Relationship(back_populates="collections")
    
    def to_collection(self) -> features_api_collection.Collection:
        collection = features_api_collection.Collection(
            id=self.id,
            title=self.title,
            description=self.description,
            links=self.links_json,
            extent=self.extent_json,
            item_type="feature",
            crs=self.crs_json,
            storage_crs=self.storage_crs,
            storage_crs_coordinate_epoch=self.storage_crs_coordinate_epoch
        )
        
        return collection
    
    # TODO: Delete column on restart / Better solution to access endpoints from different user url (e.g. localhost:8000 and localhost)
    def pre_render(self, app_base_url: str = "") -> None:
        app_base_url = app_base_url.rstrip("/")

        link_root = {
            "url": f"{app_base_url}{ogc_api_config.routes.FEATURES}",
            "rel": "root",
            "title": "Landing page of the server as {format_name}"
        }
        
        link_self = {
            "url": f"{app_base_url}{ogc_api_config.routes.FEATURES}/collections/{self.id}",
            "rel": "self",
            "title": "This document as {format_name}"
        }
        
        link_items = {
            "url": f"{app_base_url}{ogc_api_config.routes.FEATURES}/collections/{self.id}/items",
            "rel": "items",
            "title": f"Items of '{self.title}' as {{format_name}}"
        }
        
        links_json = pre_render_helper.generate_links([link_root, link_self], multiple_types=True)
        links_items = pre_render_helper.generate_multiple_link_types(link_items, formats=["geojson", "html"])
        
        links_json.extend(links_items)
        
        if self.license is not None:
            links_json.append(pre_render_helper.generate_link(self.license.pre_rendered_json))
            links_json.append(pre_render_helper.generate_link(self.license.pre_rendered_json_alternate))
        
        self.links_json = links_json
        
        self.pre_rendered_json = self.to_collection().to_json()

# Following table models are Key-Value-Tables
# However since the column name "value" doesnt work (in both python, DBeaver), we use "data" instead
class PreRenderedJson(CoreModel, table=True):
    key: str = Field(primary_key=True, unique=True)
    json_data: str

class KeyValueBase(CoreModel):
    key: str = Field(primary_key=True, unique=True)
    data: str

class GeneralOption(KeyValueBase, table=True):
    
    @classmethod
    def get_default_options(cls) -> dict:
        default_options = {
            "service_title": "OGC Features API",
            "service_description": "A OGC compliant Features API"
        }
        return default_options