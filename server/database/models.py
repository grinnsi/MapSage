import uuid

from sqlmodel import Field, SQLModel
from sqlalchemy.orm import declared_attr

from server.utils.string_utils import camel_to_snake

# All custom models should inherit from CoreModel, so they have snake_case tablenames in the sqlite db
class CoreModel(SQLModel):
    @declared_attr
    def __tablename__(cls) -> str:
        return camel_to_snake(cls.__name__)

class Connection(CoreModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, unique=True)
    name: str
    host: str
    port: int
    role: str
    password: str
    database_name: str
    
class Namespace(CoreModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, unique=True)
    name: str
    url: str

class KeyValueBase(CoreModel):
    key: str = Field(primary_key=True, unique=True)
    value: str