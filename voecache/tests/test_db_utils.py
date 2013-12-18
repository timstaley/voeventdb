from __future__ import absolute_import
import unittest
import sqlalchemy
from sqlalchemy.pool import NullPool
import sqlalchemy.orm as orm
import sqlalchemy.engine
import time

import voecache.db_utils as db_utils

from voecache.tests.config import (admin_db_url,
                                   voecache_testdb_url)

class TestDBCreateCheckDestroy(unittest.TestCase):
    def setUp(self):
        self.test_db_name = 'TemporaryUnitTestDatabase'
        self.temp_db_url = sqlalchemy.engine.url.URL(drivername='postgres',
                                        username='postgres',
                                        host='localhost',
                                        database=self.test_db_name)

    def test_check_exists(self):
        self.assertFalse(db_utils.check_database_exists(self.temp_db_url))
        self.assertTrue(db_utils.check_database_exists(admin_db_url))
        
#     @unittest.skip
    def test_create_check_delete(self):
        self.assertFalse(db_utils.check_database_exists(self.temp_db_url))
        db_utils.create_database(admin_db_url, self.test_db_name)
        self.assertTrue(db_utils.check_database_exists(self.temp_db_url),
                        'Database should be created')
        db_utils.delete_database(admin_db_url, self.test_db_name)
        self.assertFalse(db_utils.check_database_exists(self.temp_db_url),
                         "Database should be deleted again")

