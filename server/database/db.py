from contextlib import contextmanager
import os
import logging
from typing import Union
from uuid import UUID

from sqlalchemy import Engine, text, exc
from sqlmodel import SQLModel, Session, create_engine, delete, select

from server.database.models import Connection, Namespace

# local logger
_LOGGER = logging.getLogger("database")

# Initialize SQLite database engine gets called twice when starting
def init_sqlite_engine(sqlite_file_name: str, debug_mode: bool) -> Engine:
    """
    Initialize the SQLite database engine. If the database directory does not exist, it will be created.\n
    If method called before setting environment variable APP_DATABASE_DIR, it will return None.\n
    Never call this method manually. Only intended to be called by Database class.
    """
    
    database_path = os.getenv("APP_DATABASE_DIR")
    if database_path is None:
        return None
    
    if not os.path.exists(database_path):
        try:
            os.makedirs(database_path)
        except OSError:
            _LOGGER.critical(msg="Error while creating database directory; Exiting program", exc_info=debug_mode)
            raise

    sqlite_url = f"sqlite:///{database_path}{os.path.sep}{sqlite_file_name}"
    connection_args = {"check_same_thread": False}
    return create_engine(sqlite_url, echo=debug_mode, connect_args=connection_args)

# TODO How to include second db ?
class Database():
    debug_mode = os.getenv("APP_DEBUG_MODE", "False") == "True"
    sqlite_file_name = "data.db"
    sqlite_engine: Engine = init_sqlite_engine(sqlite_file_name, debug_mode)

    def __init__(self):
        raise RuntimeError("Database class cannot be instantiated")

    @classmethod
    def init_sqlite_db(cls, reset_db: bool) -> None:
        # Fallback if database engine not found (init_sqlite_engine called before setting APP_DATABASE_DIR)
        if cls.sqlite_engine is None:
            return

        _LOGGER.info(msg="Initializing SQLite database")
            
        # FIXME: Replace with cli option
        if reset_db:            
            _LOGGER.info(msg="Resetting database")
            with Session(cls.sqlite_engine) as session:
                stmt = delete(Connection)
                session.exec(stmt)
                stmt = delete(Namespace)
                session.exec(stmt)
                session.commit()
                
        _LOGGER.info(msg="Creating database tables")

        SQLModel.metadata.create_all(cls.sqlite_engine)

    @classmethod
    @contextmanager
    def get_sqlite_session(cls):
        if cls.sqlite_engine is None:
            _LOGGER.error(msg=f"Error while getting session, database engine not found", exc_info=cls.debug_mode)
            raise RuntimeError("Database engine not found")
        
        with Session(cls.sqlite_engine) as session:
            yield session
    
    @classmethod
    def get_postgresql_connection_string(cls, data: dict) -> str:
        return f"postgresql+psycopg://{data['role']}:{data['password']}@{data['host']}:{data['port']}/{data['database_name']}"

    # Input connection parameters and returns if connection is successful
    @classmethod
    def test_pg_connection(cls, data: dict) -> bool:
        """Test the connection to a PostgreSQL database, using the connection parameters"""
        pg_url = cls.get_postgresql_connection_string(data)
        pg_engine = create_engine(pg_url, echo=cls.debug_mode)
        
        connection_successful = False
        with Session(pg_engine) as session:
            try:
                stmt = select(text(" * FROM information_schema.tables"))
                result = session.exec(stmt)
                connection_successful = len(result.all()) > 0
            except exc.OperationalError as e:
                _LOGGER.debug(msg=f"Error while testing PostgreSQL connection: {e}")
                connection_successful = False
            
        _LOGGER.debug(msg=f"Result of PostgreSQL connection test: {connection_successful}")
        return connection_successful

    @classmethod
    def select_sqlite_db(cls, table_model: SQLModel = None, uuid: str = None, select_all: bool = True, statement = None) -> Union[SQLModel, list[SQLModel]]:
        with cls.get_sqlite_session() as session:
            result = None
            
            if table_model is not None and uuid is not None:
                uuid = UUID(uuid)
                result = session.get(table_model, uuid)
            elif table_model is not None and select_all:
                result = session.exec(select(table_model)).all()
            elif statement is not None:
                result = session.exec(statement).all()
            else:
                raise AttributeError("SQL-Select: Wrong combination of parameters")
            
            _LOGGER.debug(msg=f"Result of select query: {result}")
            
            if not result:
                return []
            
            return result
        
    @classmethod
    def insert_sqlite_db(cls, data_object: Union[SQLModel, list[SQLModel]] = None) -> Union[SQLModel, list[SQLModel]]:
        with cls.get_sqlite_session() as session:
            if data_object is not None:
                if type(data_object) is list:
                    session.add_all(data_object)
                    session.commit()
                    
                    for obj in data_object:
                        session.refresh(obj)
                        
                        _LOGGER.debug(msg=f"Successfully inserted [{obj.__class__.__name__}]: {obj}")
                else:
                    session.add(data_object)
                    session.commit()
                    session.refresh(data_object)
            
                    _LOGGER.debug(msg=f"Successfully inserted [{data_object.__class__.__name__}]: {data_object}")

                return data_object
            
            raise AttributeError("SQL-Insert: No data object provided")
        
    @classmethod
    def delete_sqlite_db(cls, table_model: SQLModel, uuid: str) -> Union[None, SQLModel]:
        uuid = UUID(uuid)

        with cls.get_sqlite_session() as session:
            object_to_delete = session.get(table_model, uuid)
            if not object_to_delete:
                _LOGGER.warning(msg=f"No [{table_model.__class__.__name__}] found with uuid: {uuid}")
                return None
            
            session.delete(object_to_delete)
            session.commit()
            
            _LOGGER.debug(msg=f"Successfully deleted [{table_model.__class__.__name__}]: {object_to_delete}")
            
            return object_to_delete