from __future__ import absolute_import
from sqlalchemy import create_engine
from voeventcache.tests.config import admin_db_url, testdb_empty_url
from voeventcache.database import db_utils, db_session
from voeventcache.database.models import Base

import pytest


# Would like to use 'session' scoped fixture - i.e. create once for all
# unit-tests.
# But for some reason it still gets called a second time (before destruction of
# first fixture!) and we hit a database contention lock-up.
# For now, we just make it module-level.
#
@pytest.yield_fixture(scope='module')
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
    # Create tables (will be rolled back to clean)
    Base.metadata.create_all(connection)
    # Return to test function
    yield connection
    # TearDown
    transaction.rollback()
    connection.close()
    engine.dispose()


@pytest.yield_fixture
def empty_db_session(empty_db_connection):
    """
    Provide a Session connected to the empty database.

    We use nested transactions to return the database to empty after each test.
    """
    nested_transaction = empty_db_connection.begin_nested()
    db_session.configure(bind=empty_db_connection)
    yield db_session
    db_session.remove()
    nested_transaction.rollback()
