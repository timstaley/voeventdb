from __future__ import absolute_import
import getpass

from sqlalchemy.engine.url import URL

default_username = getpass.getuser()
default_password = default_username
drivername = 'postgres'
default_host = 'localhost'

default_admin_db_params = dict(drivername=drivername,
                       username=default_username,
                       password=default_password,
                       host=default_host,
                       database=default_username)
default_admin_db_url = URL(**default_admin_db_params)


def make_db_url(admin_db_params, dbname):
    db_params = admin_db_params.copy()
    db_params['database'] = dbname
    return URL(**db_params)

def make_testdb_url(dbsuffix):
    dbprefix = '_voecache_test_'
    dbname = dbprefix + dbsuffix
    return make_db_url(default_admin_db_params, dbname)

testdb_temp_url = make_testdb_url('temp')
testdb_empty_url = make_testdb_url('empty')
testdb_corpus_url = make_testdb_url('corpus')
testdb_scratch_url = make_testdb_url('scratch')