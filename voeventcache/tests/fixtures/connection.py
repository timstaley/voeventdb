from __future__ import absolute_import
from sqlalchemy import create_engine
from voeventcache.database.models import Base
import unittest

def create_tables_and_begin_transaction(testdb_url):
    # Maybe overkill, but a neat trick, cf:
    # http://alextechrants.blogspot.co.uk/2013/08/unit-testing-sqlalchemy-apps.html
    # We use a connection-level (non-ORM) transaction that encloses everything
    # **including the table creation**.
    # This ensures that the models and queries are always in sync for testing.
    engine = create_engine(testdb_url)
    connection = engine.connect()
    transaction = connection.begin()
    #Ensure that the database is being created against t
    Base.metadata.create_all(connection)
    return engine, connection, transaction


