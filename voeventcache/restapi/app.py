#!/usr/bin/env python
"""
Fires up the REST API in debug mode for development.
"""
from voeventcache.database import db_session
from voeventcache.restapi.custom import apiv0
from voeventcache.tests.config import testdb_scratch_url
from sqlalchemy import engine
from flask import Flask


app = Flask(__name__)
app.register_blueprint(apiv0)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    db_session.configure(bind=engine.create_engine(testdb_scratch_url))
    app.run(debug=True)
