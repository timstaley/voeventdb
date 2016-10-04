from __future__ import absolute_import, unicode_literals
import getpass
import os
import subprocess

import os
on_rtd = (os.environ.get('READTHEDOCS', None) == 'True')

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


pg_sharedir = subprocess.check_output(['pg_config', '--sharedir']).strip()
q3c_batchfile_path = os.path.join(pg_sharedir, b'contrib', b'q3c.sql')

if not on_rtd:
    try:
        with open(q3c_batchfile_path) as f:
            _q3c_batch_raw = f.readlines()
            # We do our own transaction management,
            # so we ditch the 'BEGIN' and 'END' statements from q3c.sql
            q3c_batch = ''.join(_q3c_batch_raw[2:-2])
    except IOError as e:
        raise IOError(
            str(e) +
            "\nCould not find q3c batchfile at {}, have you installed q3c?".format(
                q3c_batchfile_path
            ))

testdb_temp_url = make_testdb_url('temp')
testdb_empty_url = make_testdb_url('empty')
testdb_corpus_url = make_testdb_url('corpus')
testdb_scratch_url = make_testdb_url('scratch')