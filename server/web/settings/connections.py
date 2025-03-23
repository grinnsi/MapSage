from typing import Union
from flask import Response

from server.database import models
from server.database.db import Database

def get_connections() -> Response:
    """Gets all connections to a (PostgreSQL) database from the internal database and returns a Response with the data and status"""
    
    results: Union[list[models.Dataset], None] = Database.select_sqlite_db(table_model=models.Dataset, select_all=True)

    if not results:
        results = []

    json_data = []
    
    for dataset in results:
        dataset_dict = dataset.to_dict()
        json_data.append(dataset_dict)

    json_data.sort(key=lambda x: x["name"])
    return json_data

def create_new_connection(form: dict) -> Response:
    """Creates a new database connection to a (PostgreSQL) database and stores the parameters in the internal database"""
    
    test_successful = Database.test_pg_connection(form)
    
    if test_successful:
        form["type"] = models.Dataset.Type.DB
        new_connection: models.Dataset = models.Dataset.from_dict(form)       
        new_connection = Database.insert_sqlite_db(data_object=new_connection)
        if new_connection is None:
            return Response(status=500, response="Error while inserting connection into database")

        return Response(status=201, response="Connection successfully created")
    
    return Response(status=400, response="Connection parameters incorrect")

def delete_connection(form: dict) -> Response:
    """Deletes a connection from the internal database"""
    
    connection: Union[None, models.Dataset] = Database.delete_sqlite_db(table_model=models.Dataset, primary_key_value=form["uuid"])
    if not connection:
        return Response(status=404, response="Connection not found")
    
    return Response(status=204, response="Connection successfully deleted")