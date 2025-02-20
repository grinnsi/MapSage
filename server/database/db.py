from contextlib import contextmanager
import os
import logging
from typing import Callable, Union
from uuid import UUID

from sqlalchemy import Engine, text, exc
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlmodel import SQLModel, Session, create_engine, delete, select

from server.database.models import CoreModel, GeneralOption, KeyValueBase, PreRenderedJson, TableBase
import server.database.sql_triggers as sql_triggers
from server.ogc_apis.features.implementation.static_content.licenses import get_default_licenses

# local logger
_LOGGER = logging.getLogger("database")

# Initialize SQLite database engine
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

class SetupSqliteDatabase():
    def __init__(self):
        raise RuntimeError("SetupSqliteDatabase class cannot be instantiated")
    
    @classmethod
    def get_default_db_data(cls) -> list[Callable]:
        return [
            get_default_licenses,
        ]

    @classmethod
    def setup(cls, sqlite_engine: Engine, reset_db: bool) -> None:
        # Fallback if database engine not found (init_sqlite_engine called before setting APP_DATABASE_DIR)
        if sqlite_engine is None:
            return

        _LOGGER.info(msg="Initializing SQLite database")
        
        # Drop pre_rendered_json table, so all will be generated again after restart
        with Session(sqlite_engine) as session:
            session.begin()
            session.exec(text("PRAGMA foreign_keys = ON"))
            session.exec(text(f"DROP TABLE IF EXISTS {PreRenderedJson.__tablename__}"))
            session.commit()
            
        # FIXME: Replace with cli option
        # if reset_db:            
        #     _LOGGER.info(msg="Resetting database")
        #     with Session(sqlite_engine) as session:
        #         stmt = delete(Connection)
        #         session.exec(stmt)
        #         stmt = delete(Namespace)
        #         session.exec(stmt)
        #         session.commit()
                
        _LOGGER.info(msg="Creating database tables")

        SQLModel.metadata.create_all(sqlite_engine)
        
        # Retrieve the default options from the General class
        default_options = GeneralOption.get_default_options()

        # Initialize an empty list to store existing options
        existing_options = []

        # Fetch all saved options from the database
        saved_options: list[CoreModel] = Database.select_sqlite_db(table_model=GeneralOption, select_all=True)

        # Iterate over each saved option
        for option in saved_options:
            # Check if the option key is in the default options
            if option.key in default_options:
                # If it is, add the option key to the existing options list
                existing_options.append(option.key)

        # Initialize an empty list to store options that need to be set
        options_to_set = []

        # Iterate over each key-value pair in the default options
        for k, v in default_options.items():
            # Check if the key is not in the existing options
            if k not in existing_options:
                # If it is not, create a new GeneralOption object and add it to the options_to_set list
                options_to_set.append(GeneralOption(key=k, value=v))

        # Insert the new options into the database
        Database.insert_sqlite_db(options_to_set)
        
        # Create all triggers in database
        # Drops them first, if reset_db param is True
        all_sql_triggers = sql_triggers.get_all_triggers()
        with Session(sqlite_engine) as session:
            session.begin()
            for trigger in all_sql_triggers:
                if reset_db:
                    session.exec(text(trigger[0]))
                session.exec(text(trigger[1]))
            session.commit()
            
        # Insert default data into database
        functions = cls.get_default_db_data()
        for function in functions:
            data = function()
            Database.insert_sqlite_db(data, do_nothing_on_conflict=True)

# TODO How to include second db ?
class Database():
    debug_mode = os.getenv("APP_DEBUG_MODE", "False") == "True"
    sqlite_file_name = "data.db"
    sqlite_engine: Engine = init_sqlite_engine(sqlite_file_name, debug_mode)

    def __init__(self):
        raise RuntimeError("Database class cannot be instantiated")

    @classmethod
    def init_sqlite_db(cls, reset_db: bool) -> None:
        SetupSqliteDatabase.setup(cls.sqlite_engine, reset_db)

    @classmethod
    @contextmanager
    def get_sqlite_session(cls):
        if cls.sqlite_engine is None:
            _LOGGER.error(msg=f"Error while getting session, database engine not found", exc_info=cls.debug_mode)
            raise RuntimeError("Database engine not found")
        
        with Session(cls.sqlite_engine) as session:
            yield session
    
    @classmethod
    def get_postgresql_connection_string(cls, data: dict, include_psycopg: bool = False) -> str:
        prefix = "postgresql+psycopg" if include_psycopg else "postgresql"
        return f"{prefix}://{data['role']}:{data['password']}@{data['host']}:{data['port']}/{data['database_name']}"

    # Input connection parameters and returns if connection is successful
    @classmethod
    def test_pg_connection(cls, data: dict) -> bool:
        """Test the connection to a PostgreSQL database, using the connection parameters"""
        pg_url = cls.get_postgresql_connection_string(data, include_psycopg=True)
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
    def select_sqlite_db(cls, table_model: CoreModel = None, primary_key_value: str = None, select_all: bool = True, statement = None) -> Union[CoreModel, list[CoreModel], None]:
        with cls.get_sqlite_session() as session:
            result = None
            
            if table_model is not None and primary_key_value is not None:
                if issubclass(table_model, TableBase):
                    primary_key_value = UUID(primary_key_value)
                    
                result = session.get(table_model, primary_key_value)
            elif table_model is not None and select_all:
                result = session.exec(select(table_model)).all()
            elif statement is not None:
                result = session.exec(statement).all()
            else:
                raise AttributeError("SQL-Select: Wrong combination of parameters")
            
            _LOGGER.debug(msg=f"Result of select query: {result}")
            
            if isinstance(result, list) and len(result) == 1:
                result = result[0]
            
            return result
        
    @classmethod
    def insert_sqlite_db(cls, data_object: Union[CoreModel, list[CoreModel]] = None, do_nothing_on_conflict: bool = False) -> Union[CoreModel, list[CoreModel]]:
        with cls.get_sqlite_session() as session:
            if data_object is None:
                raise AttributeError("SQL-Insert: No data object provided")
                
            if type(data_object) is list:
                if not do_nothing_on_conflict:
                    session.add_all(data_object)
                    session.commit()
                    
                    for obj in data_object:
                        session.refresh(obj)
                        
                        _LOGGER.debug(msg=f"Successfully inserted [{obj.__class__.__name__}]: {obj}")

                else:
                    # Using pg_insert to be able to use on_conflict_do_nothing
                    values = [obj.model_dump(by_alias=True, exclude_unset=True) for obj in data_object]
                    statement = pg_insert(data_object[0].__class__).values(values).on_conflict_do_nothing()
                    session.exec(statement)
                    session.commit()
                    
                    _LOGGER.debug(msg=f"Successfully inserted [{data_object[0].__class__.__name__}]: {values}")
            else:
                if not do_nothing_on_conflict:
                    session.add(data_object)
                    session.commit()
                    session.refresh(data_object)
                else:
                    values = data_object.model_dump(by_alias=True, exclude_unset=True)
                    statement = pg_insert(data_object.__class__).values(values).on_conflict_do_nothing()
                    session.exec(statement)
                    session.commit()
        
                _LOGGER.debug(msg=f"Successfully inserted [{data_object.__class__.__name__}]: {data_object}")

            return data_object
        
    @classmethod
    def delete_sqlite_db(cls, table_model: CoreModel, uuid: str) -> Union[None, CoreModel]:
        uuid = UUID(uuid)

        with cls.get_sqlite_session() as session:
            object_to_delete = session.get(table_model, uuid)
            if not object_to_delete:
                _LOGGER.warning(msg=f"No [{table_model.__class__.__name__}] found with uuid: {uuid}")
                return None
            
            session.delete(object_to_delete)
            session.commit()
            
            _LOGGER.debug(msg=f"Successfully deleted [{table_model.__class__.__name__}] with uuid [{uuid}]: {object_to_delete}")
            
            return object_to_delete
    
    @classmethod
    def update_sqlite_db(cls, update: Union[CoreModel, list[CoreModel]], primary_key_value: str = None, primary_key_name = "uuid") -> Union[None, CoreModel, list[CoreModel]]:                
        with cls.get_sqlite_session() as session:
            if type(update) is list:
                table_model = update[0].__class__
                if issubclass(table_model, KeyValueBase):
                    primary_key_name = "key"
                
                db_models = [session.get(table_model, getattr(model, primary_key_name)) for model in update]
                if len(db_models) == 0:
                    _LOGGER.warning(msg=f"No [{table_model.__class__.__name__}'s] found with uuids: {[getattr(model, primary_key_name) for model in update]}")
                    return None
                
                for db_model in db_models:
                    for update_model in update:
                        if getattr(update_model, primary_key_name) == getattr(db_model, primary_key_name):
                            new_data = update_model.model_dump(exclude_unset=True)
                            db_model.sqlmodel_update(new_data)
                            session.add(db_model)

                session.commit()
                for db_model in db_models:
                    session.refresh(db_model)
                
                _LOGGER.debug(msg=f"Successfully updated [{table_model.__class__.__name__}]: {update}")
                
                return db_models
      
            else:
                if not primary_key_value:
                    raise AttributeError("SQL-Update: No primary key value provided")
                
                table_model = update.__class__
                if issubclass(table_model, KeyValueBase):
                    primary_key_name = "key"
                    
                if primary_key_name == "uuid":
                    primary_key_value = UUID(primary_key_value)
                
                db_model: CoreModel = session.get(table_model, primary_key_value)
                if not db_model:
                    _LOGGER.warning(msg=f"No [{table_model.__class__.__name__}] found with {primary_key_name}: {primary_key_value}")
                    return None
                
                new_data = update.model_dump(exclude_unset=True)
                db_model.sqlmodel_update(new_data)
                session.add(db_model)
                session.commit()
                session.refresh(db_model)
                
                _LOGGER.debug(msg=f"Successfully updated [{table_model.__class__.__name__}] with {primary_key_name} [{primary_key_value}]: {db_model}")
                
                return db_model