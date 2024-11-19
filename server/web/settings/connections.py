from flask import Response
from sqlalchemy import create_engine

from ...database.models import Connection
from ...database.db import Database

def create_new_connection(form: Connection) -> Response:
    """Creates a new database connection to a (PostgreSQL) database and stores the parameters in the internal database"""
    test_successful = Database.test_pg_connection(form)