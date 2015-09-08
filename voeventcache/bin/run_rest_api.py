"""
Fires up the REST API in debug mode for development.
"""
from voeventcache import restapi
from voeventcache.tests.config import testdb_corpus_url

restapi.app.config['DEBUG'] = True
restapi.app.config['SQLALCHEMY_DATABASE_URI'] = testdb_corpus_url

if __name__ == '__main__':
    restapi.app.run()
