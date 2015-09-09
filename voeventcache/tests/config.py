from __future__ import absolute_import
import sqlalchemy.engine
import getpass

from sqlalchemy.engine import create_engine
from sqlalchemy.engine.url import URL
from sqlalchemy.orm import sessionmaker

db_username = getpass.getuser()
db_password = db_username
drivername = 'postgres'
host = 'localhost'

admin_db_params = dict(drivername=drivername,
                       username=db_username,
                       password=db_password,
                       host=host,
                       database=db_username)
admin_db_url = URL(**admin_db_params)


testdb_temp_params = admin_db_params.copy()
testdb_temp_params['database'] = '_voecache_test_temp'
testdb_temp_url = URL(**testdb_temp_params)

testdb_empty_params = admin_db_params.copy()
testdb_empty_params['database'] = '_voecache_test_empty'
testdb_empty_url = URL(**testdb_empty_params)

testdb_corpus_params = admin_db_params.copy()
testdb_corpus_params['database'] = '_voecache_test_corpus'
testdb_corpus_url = URL(**testdb_corpus_params)

testdb_scratch_params = admin_db_params.copy()
testdb_scratch_params['database'] = '_voecache_test_manual'
testdb_scratch_url = URL(**testdb_scratch_params)