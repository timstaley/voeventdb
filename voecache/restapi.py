from __future__ import absolute_import
from flask import Flask
import flask.ext.sqlalchemy

from voecache import ingest, db_utils
from voecache.tests.config import voecache_corpusdb_url, admin_db_url
from voecache.models import Base, Voevent

from flask.ext.restless import APIManager

url_prefix = '/api/v0'

app = Flask(__name__)

db = flask.ext.sqlalchemy.SQLAlchemy(app)

manager = APIManager(app, flask_sqlalchemy_db=db)

voevent_blueprint = manager.create_api(Voevent,
                                       url_prefix=url_prefix,
                                       methods=['GET'])

