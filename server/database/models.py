import uuid

from sqlmodel import Field, SQLModel

class Connection(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, unique=True)
    name: str
    host: str
    port: int
    role: str
    password: str
    database_name: str
    
class Namespace(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, unique=True)
    name: str
    url: str