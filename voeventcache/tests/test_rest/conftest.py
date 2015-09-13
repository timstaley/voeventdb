import pytest
from voeventcache.tests.fixtures.connection import (
    empty_db_connection,
    empty_db_session
)

from voeventcache.restapi.app import app

@pytest.yield_fixture
def flask_test_client():
    print
    print "setting up flask client"
    app.testing = True
    client = app.test_client()
    app_context = app.test_request_context()
    app_context.push()
    yield client
    app_context.pop()
    del app_context