from __future__ import absolute_import
import iso8601
from flask import (
    Blueprint, jsonify, abort, request, make_response, redirect
)
from flask.views import View
from flask import url_for

from voeventcache.database import session_registry as db_session
from voeventcache.database.models import Voevent
import voeventcache.database.convenience as convenience
import voeventcache.database.query as query

apiv0 = Blueprint('apiv0', __name__,
                  url_prefix='/apiv0')


class QueryKeys:
    authored_since = 'authored_since'
    authored_until = 'authored_until'
    prefix = 'prefix'
    contains = 'contains'
    stream = 'stream'


class ResultKeys:
    count = 'count'
    endpoint = 'endpoint'
    querystring = 'querystring'
    result = 'result'
    url = 'url'


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


class QueryView(View):
    def get_query(self):
        raise NotImplementedError

    def process_query(self, q):
        raise NotImplementedError

    def dispatch_request(self):
        q = self.get_query()
        q = filter_query(q, request.args)
        result = self.process_query(q)
        resultdict = {
            ResultKeys.result: result,
            ResultKeys.querystring: request.args,
            ResultKeys.url: request.url,
            ResultKeys.endpoint: request.url_rule.rule,
        }
        return jsonify(resultdict)


def add_to_apiv0(queryview_class):
    name = queryview_class.view_name
    apiv0.add_url_rule('/' + name,
                       view_func=queryview_class.as_view(name))


# @apiv0.route('/')
# def root_redirect():
#     return redirect(url_for(apiv0.name + '.' + 'stream_count'), code=302)


class Count(QueryView):
    """
    Int: Number of packets matching querystring.

    Returns total number of packets in database if the querystring is blank.
    """
    view_name = 'count'

    def get_query(self):
        return db_session.query(Voevent)

    def process_query(self, q):
        return q.count()


add_to_apiv0(Count)


class IvornList(QueryView):
    """
    List: All ivorns matching querystring.
    """
    view_name = 'ivorn'

    def get_query(self):
        return db_session.query(Voevent.ivorn)

    def process_query(self, q):
        return q.all()


apiv0.add_url_rule('/ivorn', view_func=IvornList.as_view('ivorn'))


class MonthCount(QueryView):
    """
    Dict: Mapping month -> packet counts per-month.
    """
    view_name = 'month_count'

    def get_query(self):
        return query.month_counts_q(db_session)

    def process_query(self, q):
        raw_results = q.all()
        converted_results = []
        for r in raw_results:
            if r.month_id:
                newrow = (r.month_id.date().isoformat()[:-3], r.month_count)
            else:
                newrow = r
            converted_results.append(newrow)
        return dict(converted_results)


add_to_apiv0(MonthCount)


class RoleCount(QueryView):
    """
    Dict: Mapping role -> packet counts per-role.
    """
    view_name = 'role_count'

    def get_query(self):
        return query.role_counts_q(db_session)

    def process_query(self, q):
        return dict(q.all())


add_to_apiv0(RoleCount)


class StreamCount(QueryView):
    """
    Dict: Mapping stream -> packet counts per-stream.
    """
    view_name = 'stream_count'

    def get_query(self):
        return query.stream_counts_q(db_session)

    def process_query(self, q):
        return dict(q.all())


add_to_apiv0(StreamCount)


class StreamRoleCount(QueryView):
    """
    Nested dict: Mapping stream -> role -> packet counts per-role.
    """
    view_name = 'stream_role_count'

    def get_query(self):
        return query.stream_counts_role_breakdown_q(db_session)

    def process_query(self, q):
        return convenience.to_nested_dict(q.all())

add_to_apiv0(StreamRoleCount)

@apiv0.route('/xml/<path:ivorn>')
def get_xml(ivorn=None):
    """
    Raw xml packet for a given IVORN
    """
    if not ivorn:
        abort(400)
    xml = db_session.query(Voevent.xml).filter(
        Voevent.ivorn == ivorn
    ).scalar()
    if xml:
        r = make_response(xml)
        r.mimetype = 'text/xml'
        return r
    else:
        abort(404)
