from __future__ import absolute_import
from sqlalchemy import create_engine
from voeventcache.tests.config import admin_db_url, testdb_empty_url
from voeventcache.database import db_utils, db_session
from voeventcache.database.models import Base

import pytest
@pytest.yield_fixture(scope='session')
def empty_db_connection(request):
    """
    Connect to db, create tables and begin connection-level (outer) transaction.

    Will also create the database first if it does not exist.

    Maybe overkill, but a neat trick, cf:
    http://alextechrants.blogspot.co.uk/2013/08/unit-testing-sqlalchemy-apps.html
    We use a connection-level (non-ORM) transaction that encloses everything
    **including the table creation**.
    This ensures that the models and queries are always in sync for testing.

    Note that the transaction must be explicitly rolled back. An alternative
    approach would be to delete all tables, but presumably that would
    take slightly longer than a rollback (be interesting to check).
    """
    # Could be parameterized, but then it wouldn't make sense as a session-level fixture
    # Unless PyTest is smart enough to maintain fixtures in parallel?
    # test_db_url = getattr(request.module, "test_db_url", testdb_empty_url)
    test_db_url = testdb_empty_url
    if not db_utils.check_database_exists(test_db_url):
        db_utils.create_database(admin_db_url, test_db_url.database)
    engine = create_engine(test_db_url)
    connection = engine.connect()
    transaction = connection.begin()
    Base.metadata.create_all(connection)
    print
    print "Initializing the database"

    #Returned to test function
    yield connection
    print
    print "Tearing down the database"
    #TearDown
    transaction.rollback()
    connection.close()
    engine.dispose()
    print
    print "Disposed."


@pytest.yield_fixture
def empty_db_session(empty_db_connection):
    """
    Provide a Session connected to the empty database.

    We use nested transactions to return the database to empty after each test.
    """
    print
    print "Nesting transaction"
    nested_transaction = empty_db_connection.begin_nested()
    db_session.configure(bind=empty_db_connection)
    yield db_session
    print
    print "Cleaning up the nest"
    db_session.remove()
    nested_transaction.rollback()
