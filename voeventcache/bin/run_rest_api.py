#!/usr/bin/env python
"""
Fires up the REST API in debug mode for development.
"""
from voeventcache.restapi.restapi import rest_app, db_session
from voeventcache.tests.config import testdb_scratch_url
from sqlalchemy import engine

# The all-important link-the-db-config-to-the-flask-app step:
db_session.configure(bind=engine.create_engine(testdb_scratch_url))

rest_app.config['DEBUG'] = True

if __name__ == '__main__':
    rest_app.run()
