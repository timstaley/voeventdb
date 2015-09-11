#!/usr/bin/env python
"""
Initialize the Flask app.
"""
from voeventcache.database import db_session
from voeventcache.restapi.custom import apiv0
from voeventcache.restapi.restlessapi import restless_manager
from voeventcache.tests.config import testdb_scratch_url
from sqlalchemy import engine
from flask import Flask

app = Flask(__name__)
app.register_blueprint(apiv0)
restless_manager.init_app(app, session=db_session)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


if __name__ == '__main__':
    """
    Fires up the app in debug mode for development.
    """
    db_session.configure(bind=engine.create_engine(testdb_scratch_url))
    app.run(debug=True)
