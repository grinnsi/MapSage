from flask import Response
from sqlmodel import select

from ...database.models import Connection
from ...database.db import Database

def get_connections() -> Response:
    """Creates a new database connection to a (PostgreSQL) database and stores the parameters in the internal database"""
    result = Database.get_table_result(select(Connection))
    print(result)

def create_new_connection(form: Connection) -> Response:
    """Creates a new database connection to a (PostgreSQL) database and stores the parameters in the internal database"""
    test_successful = Database.test_pg_connection(form)
    print(test_successful)