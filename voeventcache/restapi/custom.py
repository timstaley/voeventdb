from __future__ import absolute_import
import iso8601
from flask import Blueprint, jsonify, abort, request

from voeventcache.database import db_session
from voeventcache.database.models import Voevent

apiv0 = Blueprint('apiv0', __name__,
                  url_prefix='/dev')


def filter_query(q, args):
    if 'prefix' in args:
        q = q.filter(
            Voevent.ivorn.like('{}%'.format(args['prefix'])))
    if 'authored_from' in args:
        authored_from = iso8601.parse_date(args['authored_from'])
        q = q.filter(
            Voevent.author_datetime >= authored_from)
    if 'authored_until' in args:
        authored_until = iso8601.parse_date(args['authored_until'])
        q = q.filter(
            Voevent.author_datetime <= authored_until)
    return q


@apiv0.route('/')
def hello_world():
    return 'Hello World!\n\n'


@apiv0.route('/count')
def get_count():
    q = db_session.query(Voevent)
    q = filter_query(q, request.args)
    n_matching = q.count()
    results = {'count': n_matching}
    results['query'] = request.args
    return jsonify(results)


@apiv0.route('/xml/')
@apiv0.route('/xml/<path:ivorn>')
def get_xml(ivorn=None):
    if not ivorn:
        abort(400)
    xml = db_session.query(Voevent.xml).filter(
        Voevent.ivorn == ivorn
    ).scalar()
    if xml:
        return xml
    else:
        abort(404)

