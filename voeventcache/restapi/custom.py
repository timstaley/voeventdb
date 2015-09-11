from __future__ import absolute_import
from flask import Blueprint, jsonify

from voeventcache.database import db_session
from voeventcache.database.models import Voevent

apiv0 = Blueprint('apiv0', __name__,
                  url_prefix='/dev')

@apiv0.route('/')
def hello_world():
    return 'Hello World!\n\n'

@apiv0.route('/count')
def voevents_in_database():
    n_voevent = db_session.query(Voevent).count()
    return jsonify({'count':n_voevent})