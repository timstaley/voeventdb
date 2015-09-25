import pytest
from voeventcache.tests.fixtures.connection import (
    empty_db_connection,
    fixture_db_session,
    simple_populated_db
)

from voeventcache.restapi.app import app

@pytest.yield_fixture
def flask_test_client(fixture_db_session):
    # print
    # print "setting up flask client"
    app.testing = True
    client = app.test_client()
    app_context = app.test_request_context()
    app_context.push()
    yield client
    app_context.pop()
    del app_context