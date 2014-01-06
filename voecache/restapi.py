from __future__ import absolute_import
from flask import Flask
import flask.ext.sqlalchemy
from voecache.models import Voevent
from voecache.models import Base as predeclared_base

from flask.ext.restless import APIManager

url_prefix = '/api/v0'

app = Flask(__name__)

class KludgeAlchemy(flask.ext.sqlalchemy.SQLAlchemy):
    def make_declarative_base(self):
        return predeclared_base

db = KludgeAlchemy(app)

manager = APIManager(app, flask_sqlalchemy_db=db)

voevent_blueprint = manager.create_api(Voevent,
                                       url_prefix=url_prefix,
                                       methods=['GET'])

