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


def make_testdb_url(dbsuffix):
    dbprefix = '_voecache_test_'
    db_params = admin_db_params.copy()
    db_params['database'] = dbprefix+dbsuffix
    return URL(**db_params)

testdb_temp_url = make_testdb_url('temp')
testdb_empty_url = make_testdb_url('empty')
testdb_corpus_url = make_testdb_url('corpus')
testdb_scratch_url = make_testdb_url('scratch')