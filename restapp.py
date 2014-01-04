from flask import Flask
import flask.ext.sqlalchemy

from voecache import ingest, db_utils
from voecache.tests.config import voecache_corpusdb_url, admin_db_url
from voecache.models import Base, Voevent

from flask.ext.restless import APIManager

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = voecache_corpusdb_url
db = flask.ext.sqlalchemy.SQLAlchemy(app)

manager = APIManager(app, flask_sqlalchemy_db=db)


voevent_blueprint = manager.create_api(Voevent,
                                       methods=['GET'])


if __name__ == '__main__':
    app.run()
