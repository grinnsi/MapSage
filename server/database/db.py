import os
import logging

from sqlalchemy import Engine, text
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

    # Input connection parameters and returns if connection is successful
    @classmethod
    def test_pg_connection(cls, data: dict) -> bool:
        """Test the connection to a PostgreSQL database, using the connection parameters"""
        pg_url = f"postgresql+psycopg://{data["role"]}:{data["password"]}@{data["host"]}:{data["port"]}/{data["database_name"]}"
        pg_engine = create_engine(pg_url, echo=cls.debug_mode)
        
        with Session(pg_engine) as session:
            stmt = select(text(" * FROM information_schema.tables"))
            result = session.exec(stmt)
            _LOGGER.debug(msg=f"Result of PostgreSQL connection test: {result}")
            
    @classmethod
    def select_table(cls, statement) -> list:
        if cls.sqlite_engine is None:
            _LOGGER.error(msg=f"Error while selecting table, database engine not found; Value: {cls.sqlite_engine}", exc_info=cls.debug_mode)
            return []
        with Session(cls.sqlite_engine) as session:
            results = session.exec(statement)
            return results.all()

    # @classmethod
    # def get_db(cls):
    #     if cls.sqlite_engine is None:
    #         _LOGGER.error(msg="Error while getting database, database engine not found", exc_info=cls.debug_mode)
    #         return None