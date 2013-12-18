from __future__ import absolute_import
import sqlalchemy.engine

default_db_url = sqlalchemy.engine.url.URL(drivername='postgres',
                                        username='postgres',
                                        host='localhost',
                                        database='postgres')

voecache_testdb_name = 'voecache_testdb'
voecache_testdb_url = sqlalchemy.engine.url.URL(drivername='postgres',
                                        username='postgres',
                                        host='localhost',
                                        database=voecache_testdb_name)
