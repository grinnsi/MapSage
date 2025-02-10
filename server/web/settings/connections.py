from typing import Union
from flask import Response

from server.database.models import Connection
from server.database.db import Database

def get_connections() -> Response:
    """Gets all connections to a (PostgreSQL) database from the internal database and returns a Response with the data and status"""
    
    results: list[Union[Connection, None]] = Database.select_sqlite_db(table_model=Connection, select_all=True)

    json_data = [{
        "uuid": connection.id,
        "name": connection.name,
        "host": connection.host,
        "port": connection.port,
        "role": connection.role,
        "database_name": connection.database_name
    } for connection in results if connection]

    return json_data

def create_new_connection(form: dict) -> Response:
    """Creates a new database connection to a (PostgreSQL) database and stores the parameters in the internal database"""
    
    test_successful = Database.test_pg_connection(form)
    
    if test_successful:
        new_connection: Connection = Connection(**form)        
        new_connection = Database.insert_sqlite_db(data_object=new_connection)
        if new_connection is None:
            return Response(status=500, response="Error while inserting connection into database")

        return Response(status=201, response="Connection successfully created")
    
    return Response(status=400, response="Connection parameters incorrect")

def delete_connection(form: dict) -> Response:
    """Deletes a connection from the internal database"""
    
    connection: Union[None, Connection] = Database.delete_sqlite_db(table_model=Connection, uuid=form["uuid"])
    if not connection:
        return Response(status=404, response="Connection not found")
    
    return Response(status=204, response="Connection successfully deleted")