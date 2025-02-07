from flask import Response
from sqlmodel import select

from ...database.models import Connection
from ...database.db import Database

def get_connections() -> dict:
    """Gets all connections to a (PostgreSQL) database from the internal database and returns a Response with the data and status"""
    results: list[Connection] = Database.select_table(select(Connection))
    json_data = [{
        "uuid": connection.id,
        "name": connection.name,
        "host": connection.host,
        "port": connection.port,
        "role": connection.role,
        "database_name":connection.database_name
    } for connection in results]
    
    return json_data

def create_new_connection(form: Connection) -> Response:
    """Creates a new database connection to a (PostgreSQL) database and stores the parameters in the internal database"""
    test_successful = Database.test_pg_connection(form)
    print(test_successful)