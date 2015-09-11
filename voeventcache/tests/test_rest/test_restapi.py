from __future__ import absolute_import
import unittest

from voeventcache.database import db_utils, db_session
from voeventcache.tests.config import (admin_db_url,
                                       testdb_empty_url)
from voeventcache.tests.fixtures.connection import (
    create_tables_and_begin_transaction,
)

from voeventcache.restapi.app import app
from voeventcache.restapi.custom import apiv0
import json
from flask import url_for


def setUpModule():
    if not db_utils.check_database_exists(testdb_empty_url):
        db_utils.create_database(admin_db_url, testdb_empty_url.database)
    global engine, connection, transaction
    engine, connection, transaction = create_tables_and_begin_transaction(
        testdb_empty_url)


def tearDownModule():
    ## Roll back the top level transaction and disconnect from the database
    # transaction.commit() #Leave the database around for manual inspection
    transaction.rollback()
    connection.close()
    engine.dispose()


class DBTestCase(unittest.TestCase):
    """
    Run each test-case in a nested transaction and then roll back on teardown.

    This means that each test-case runs on a fresh database as-per setUpModule.
    """

    def setUp(self):
        unittest.TestCase.setUp(self)
        self.__transaction = connection.begin_nested()
        # self.session = Session(connection)
        db_session.configure(bind=connection)
        self.session = db_session()

    def tearDown(self):
        # self.session.close()
        db_session.remove()
        self.__transaction.rollback()


class FlaskTestCase(DBTestCase):
    def setUp(self):
        super(FlaskTestCase, self).setUp()
        app.testing = True
        self.client = app.test_client()
        self._ctx = app.test_request_context()
        self._ctx.push()

    def tearDown(self):
        super(FlaskTestCase, self).tearDown()
        self._ctx.pop()
        del self._ctx

class TestWithEmptyDatabase(FlaskTestCase):
    def test_bare_root(self):
        rv = self.client.get('/')
        self.assertEqual(rv.status_code, 404)

    def test_api_root(self):
        rv = self.client.get(apiv0.url_prefix+'/')
        self.assertEqual(rv.status_code, 200)

    def test_api_count(self):
        rv = self.client.get(url_for('apiv0.voevents_in_database'))
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(json.loads(rv.data),
                         dict(count=0))
