from __future__ import absolute_import
import unittest

import sqlalchemy
import sqlalchemy.engine

import voeventcache.database.db_utils as db_utils
from voeventcache.tests.config import (admin_db_url, db_username, db_password)


class TestDBCreateCheckDestroy(unittest.TestCase):
    def setUp(self):
        self.test_db_name = '_TempUnitTestDB'
        self.test_db_url = sqlalchemy.engine.url.URL(drivername='postgres',
                                                     username=db_username,
                                                     password=db_password,
                                                     host='localhost',
                                                     database=self.test_db_name)

    def test_check_exists(self):
        self.assertFalse(db_utils.check_database_exists(self.test_db_url))
        self.assertTrue(db_utils.check_database_exists(admin_db_url))

    def test_create_check_delete(self):
        self.assertFalse(db_utils.check_database_exists(self.test_db_url))
        db_utils.create_database(admin_db_url, self.test_db_name)
        self.assertTrue(db_utils.check_database_exists(self.test_db_url),
                        'Database was not created')
        db_utils.delete_database(admin_db_url, self.test_db_name)
        self.assertFalse(db_utils.check_database_exists(self.test_db_url),
                         "Database was not deleted")
