from __future__ import absolute_import
import unittest
import sqlalchemy
from sqlalchemy.pool import NullPool
import sqlalchemy.orm as orm

from voecache.tests.config import (default_db_url, 
                                   voecache_testdb_name, 
                                   voecache_testdb_url)

def setUpModule():
    engine = sqlalchemy.create_engine(default_db_url)
    conn = engine.connect()
    conn.execute("commit")
    conn.execute("create database " + voecache_testdb_name)
    conn.close()
    engine.dispose()
    global test_engine
    test_engine = sqlalchemy.create_engine(voecache_testdb_url)
    global test_session
    test_session = orm.Session(bind=test_engine)
    

def tearDownModule():
    # Kill off any lingering sessions:
    test_session.close_all()
    test_engine.dispose()

    engine = sqlalchemy.create_engine(default_db_url)
    conn = engine.connect()
    conn.execute("commit")
    conn.execute("drop database " + voecache_testdb_name)
    conn.close()
        
# class TestDBConnection(unittest.TestCase):
#     def test_postgres_generic_connect(self):
#         engine = sqlalchemy.create_engine(default_db_url)
#         conn = engine.connect()
#         conn.close()
#
#     def test_postgres_testdb(self):
#         engine = sqlalchemy.create_engine(voecache_testdb_url)
#         conn = engine.connect()
#         conn.close()

class TestDBConnection(unittest.TestCase):
    def test_basic_select(self):
        result = test_session.execute("select 1").scalar()
        self.assertEqual(result, 1)

class TestDeclarativeSchema(unittest.TestCase):
    def test_table_create(self):
        pass
#         orm.Session(bind = )
        
