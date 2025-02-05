import os
import logging

from sqlalchemy import Engine, text
from sqlmodel import SQLModel, Session, create_engine, delete, select 

from server.database.models import Connection, Namespace

# TODO How to include second db ?
class Database():
    # FIXME Do a global logger
    logger = logging.getLogger()
    debug_mode = False
    sqlite_engine: Engine = None
    sqlite_file_name = "data.db"

    @classmethod
    def init_sqlite_db(cls, debug_mode: bool, reset_db: bool) -> None:
        cls.debug_mode = debug_mode
        database_path = os.getenv("APP_DATABASE_DIR")
        if not os.path.exists(database_path):
            try:
                os.makedirs(database_path)
            except OSError:
                cls.logger.critical(msg="Error while creating database directory; Exiting program", exc_info=cls.debug_mode)
                raise

        sqlite_url = f"sqlite:///{database_path}{os.path.sep}{cls.sqlite_file_name}"
        engine = create_engine(sqlite_url, echo=cls.debug_mode)
        
        if reset_db:
            with Session(engine) as session:
                stmt = delete(Connection)
                session.exec(stmt)
                stmt = delete(Namespace)
                session.exec(stmt)
                session.commit()

        SQLModel.metadata.create_all(engine)
        cls.sqlite_engine = engine

    # Input connection parameters and returns if connection is successful
    @classmethod
    def test_pg_connection(cls, data: dict) -> bool:
        """Test the connection to a PostgreSQL database, using the connection parameters"""
        pg_url = f"postgresql+psycopg://{data["role"]}:{data["password"]}@{data["host"]}:{data["port"]}/{data["database_name"]}"
        pg_engine = create_engine(pg_url, echo=cls.debug_mode)
        
        with Session(pg_engine) as session:
            stmt = select(text(" * FROM information_schema.tables"))
            result = session.exec(stmt)
            cls.logger.debug(msg=f"Result of PostgreSQL connection test: {result}")
            
    @classmethod
    def select_table(cls, statement) -> list:
        with Session(cls.sqlite_engine) as session:
            results = session.exec(statement)
            return results.all()

    # @classmethod
    # def get_db(cls):
    #     if cls.sqlite_engine is None:
    #         cls.logger.error(msg="Error while getting database, database engine not found", exc_info=cls.debug_mode)
    #         return None