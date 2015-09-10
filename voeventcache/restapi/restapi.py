from __future__ import absolute_import
from flask import Flask, jsonify

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from voeventcache.database.models import Voevent

rest_app = Flask(__name__)

#Use the 'magic' sqlalchemy thread-local-singleton session-maker/session-proxy thing.
#Configure this with an engine of choice before instantiating
db_session = scoped_session(sessionmaker())

@rest_app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

@rest_app.route('/')
def hello_world():
    return 'Hello World!\n\n'

@rest_app.route('/count')
def voevents_in_database():
    n_voevent = db_session.query(Voevent).count()
    return jsonify({'count':n_voevent})