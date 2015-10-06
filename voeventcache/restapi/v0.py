from __future__ import absolute_import
import iso8601
from flask import Blueprint, jsonify, abort, request

from datetime import datetime

from voeventcache.database import session_registry as db_session
from voeventcache.database.models import Voevent
import voeventcache.database.convenience as convenience
import voeventcache.database.query as query

apiv0 = Blueprint('apiv0', __name__,
                  url_prefix='/v0')


class QueryKeys:
    authored_since = 'authored_since'
    authored_until = 'authored_until'
    prefix = 'prefix'
    contains = 'contains'
    stream = 'stream'


class ResultKeys:
    count = 'count'
    count_by_month = 'count_by_month'
    ivorn = 'ivorn'
    query = 'query'
    role = 'role'
    role_by_stream = 'role_by_stream'
    stream = 'stream'


def filter_query(q, args):
    keys = QueryKeys
    if keys.authored_since in args:
        authored_since = iso8601.parse_date(args[keys.authored_since])
        q = q.filter(Voevent.author_datetime >= authored_since)
    if keys.authored_until in args:
        authored_until = iso8601.parse_date(args[keys.authored_until])
        q = q.filter(Voevent.author_datetime <= authored_until)
    if keys.contains in args:
        q = q.filter(Voevent.ivorn.like('%{}%'.format(args[keys.contains])))
    if keys.prefix in args:
        q = q.filter(Voevent.ivorn.like('{}%'.format(args[keys.prefix])))
    if keys.stream in args:
        q = q.filter(Voevent.stream == args[keys.stream])
    return q


@apiv0.route('/')
@apiv0.route('/stream')
def streamcounts():
    q = query.stream_counts_q(db_session)
    q = filter_query(q, request.args)
    return jsonify({
        ResultKeys.stream: dict(q.all()),
        ResultKeys.query : request.args,
    })


@apiv0.route('/breakdown')
def breakdown():
    q = query.stream_counts_role_breakdown_q(db_session)
    q = filter_query(q, request.args)
    results = convenience.to_nested_dict(q.all())

    return jsonify({
        ResultKeys.role_by_stream: results,
        ResultKeys.count: len(results),
        ResultKeys.query : request.args,
    })


@apiv0.route('/count')
def count_matching():
    q = db_session.query(Voevent)
    q = filter_query(q, request.args)
    results = {
        ResultKeys.count: q.count(),
        ResultKeys.query: request.args
    }
    return jsonify(results)

@apiv0.route('/count_by_month')
def count_matching_by_month():
    q = query.month_counts_q(db_session)
    q = filter_query(q, request.args)
    results = q.all()
    converted_results = []
    for r in results:
        if r.month_id:
            newrow = (r.month_id.date().isoformat()[:-3], r.month_count)
        else:
            newrow = r
        converted_results.append(newrow)

    return jsonify({
        ResultKeys.count_by_month: converted_results,
        ResultKeys.query: request.args
    })



@apiv0.route('/ivorn')
def ivorns_matching():
    q = db_session.query(Voevent.ivorn)
    q = filter_query(q, request.args)
    ivorns = q.all()
    results = {
        ResultKeys.ivorn: ivorns,
        ResultKeys.count: len(ivorns),
        ResultKeys.query: request.args
    }
    return jsonify(results)


@apiv0.route('/role')
def roles():
    q = query.role_counts_q(db_session)
    q = filter_query(q, request.args)
    return jsonify({
        ResultKeys.role: dict(q.all()),
        ResultKeys.query: request.args
    })


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
