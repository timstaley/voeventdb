"""
Fires up the REST API in debug mode for development.
"""
from voeventcache.restapi.restlessapi import restless_app
from voeventcache.tests.config import testdb_corpus_url

restless_app.config['DEBUG'] = True
restless_app.config['SQLALCHEMY_DATABASE_URI'] = testdb_corpus_url

if __name__ == '__main__':
    restless_app.run()
