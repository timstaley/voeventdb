from __future__ import absolute_import
import sqlalchemy.engine


admin_db_url = sqlalchemy.engine.url.URL(drivername='postgres',
                                        username='postgres',
                                        host='localhost',
                                        database='postgres')

voecache_testdb_url = sqlalchemy.engine.url.URL(drivername='postgres',
                                        username='postgres',
                                        host='localhost',
                                        database='voecache_test')

voecache_corpusdb_url = sqlalchemy.engine.url.URL(drivername='postgres',
                                        username='postgres',
                                        host='localhost',
                                        database='voecache_corpus')
