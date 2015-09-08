from __future__ import absolute_import
import unittest

import sqlalchemy
import sqlalchemy.engine

import voeventcache.database.db_utils as db_utils
from voeventcache.tests.config import (admin_db_url, testdb_temp_url)


class TestDBCreateCheckDestroy(unittest.TestCase):
    def test_check_exists(self):
        self.assertFalse(db_utils.check_database_exists(testdb_temp_url))
        self.assertTrue(db_utils.check_database_exists(admin_db_url))

    def test_create_check_delete(self):
        self.assertFalse(db_utils.check_database_exists(testdb_temp_url))
        db_utils.create_database(admin_db_url, testdb_temp_url.database)
        self.assertTrue(db_utils.check_database_exists(testdb_temp_url),
                        'Database was not created')
        db_utils.delete_database(admin_db_url, testdb_temp_url.database)
        self.assertFalse(db_utils.check_database_exists(testdb_temp_url),
                         "Database was not deleted")
