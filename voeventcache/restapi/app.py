#!/usr/bin/env python
"""
Initialize the Flask app.
"""
from voeventcache.database import session_registry
from voeventcache.restapi.v0 import apiv0
from voeventcache.restapi.restlessapi import restless_manager
from voeventcache.tests.config import testdb_scratch_url, testdb_corpus_url
from sqlalchemy import engine
from flask import Flask

app = Flask(__name__)
app.register_blueprint(apiv0)
# restless_manager.init_app(app, session=session_registry)


@app.teardown_appcontext
def shutdown_session(exception=None):
    session_registry.remove()


if __name__ == '__main__':
    """
    Fires up the app in debug mode for development.
    """
    session_registry.configure(bind=engine.create_engine(testdb_corpus_url))
    app.run(debug=True)
