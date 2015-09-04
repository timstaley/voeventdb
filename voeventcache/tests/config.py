from __future__ import absolute_import
import sqlalchemy.engine
import getpass
db_username = getpass.getuser()
db_password = db_username
drivername = 'postgres'
host = 'localhost'

admin_db_url = sqlalchemy.engine.url.URL(drivername=drivername,
                                        username=db_username,
                                        password=db_password,
                                        host=host,
                                        database=db_username)

voecache_testdb_url = sqlalchemy.engine.url.URL(drivername=drivername,
                                        username=db_username,
                                        password=db_password,
                                        host=host,
                                        database='_voecache_test')

voecache_corpusdb_url = sqlalchemy.engine.url.URL(drivername=drivername,
                                        username=db_username,
                                        password=db_password,
                                        host=host,
                                        database='voecache_corpus')
