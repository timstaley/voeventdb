from __future__ import absolute_import

import voeventdb.database.db_utils as db_utils
from voeventdb.tests.config import (admin_db_url, testdb_temp_url)

class TestDBCreateCheckDestroy:
    def test_starting_conditions(self):
        # Make sure we have access to an admin database, and the tempdb
        # has not already been created.
        assert db_utils.check_database_exists(testdb_temp_url) == False
        assert db_utils.check_database_exists(admin_db_url) == True

    def test_create_check_delete(self):
        # DB should be absent to start off with
        assert db_utils.check_database_exists(testdb_temp_url) == False
        # Now create it
        db_utils.create_database(admin_db_url, testdb_temp_url.database)
        assert db_utils.check_database_exists(testdb_temp_url) == True
        # And delete it again
        db_utils.delete_database(admin_db_url, testdb_temp_url.database)
        assert db_utils.check_database_exists(testdb_temp_url) == False

