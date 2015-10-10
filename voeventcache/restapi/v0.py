from __future__ import absolute_import
import iso8601
from flask import (
    Blueprint, jsonify, abort, request, make_response,
    current_app
)
from flask.views import View
from flask import url_for

from sqlalchemy import or_, and_

from voeventcache.database import session_registry as db_session
from voeventcache.database.models import Voevent
import voeventcache.database.convenience as convenience
import voeventcache.database.query as query

apiv0 = Blueprint('apiv0', __name__,
                  url_prefix='/apiv0')

default_query_limit = 100


class QueryKeys:
    authored_since = 'authored_since'
    """
    Return only VOEvents with a ``Who.Date`` entry dated after the given time.

    Date-time strings passed should be in a format parseable by the
    ``is08601.parse_date`` function e.g.::

        authored_since=2015-10-09T21:34:19

    or::

        authored_since=2015-10-09

    """
    authored_until = 'authored_until'
    contains = 'contains'
    limit = 'limit'
    offset = 'offset'
    prefix = 'prefix'
    role = 'role'
    stream = 'stream'


class ResultKeys:
    count = 'count'
    endpoint = 'endpoint'
    limit = 'limit'
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
        q = q.filter(
            and_(
                Voevent.ivorn.like('%{}%'.format(substr))
                for substr in args.getlist(keys.contains)
            )
        )
    if keys.prefix in args:
        q = q.filter(
            or_(
                Voevent.ivorn.like('{}%'.format(pref))
                for pref in args.getlist(keys.prefix)
            )
        )
    if keys.role in args:
        q = q.filter(Voevent.role == args[keys.role])
    if keys.stream in args:
        q = q.filter(Voevent.stream == args[keys.stream])
    return q


def make_response_dict(result):
        resultdict = {
            ResultKeys.endpoint: request.url_rule.rule,
            ResultKeys.querystring: dict(request.args.lists()),
            ResultKeys.result: result,
            ResultKeys.url: request.url,
        }
        return resultdict

class QueryView(View):
    def get_query(self):
        raise NotImplementedError

    def process_query(self, q):
        raise NotImplementedError

    def dispatch_request(self):
        q = self.get_query()
        q = filter_query(q, request.args)
        result = self.process_query(q)
        return jsonify(make_response_dict(result))


class ListQueryView(View):
    def get_query(self):
        raise NotImplementedError

    def dispatch_request(self):
        limit = request.args.get(QueryKeys.limit, None)
        if not limit:
            limit = current_app.config.get('DEFAULT_QUERY_LIMIT',
                                           default_query_limit)
        q = self.get_query()
        q = filter_query(q, request.args)
        q = q.limit(limit)
        q = q.offset(request.args.get(QueryKeys.offset))
        result = q.all()
        resultdict = make_response_dict(result)
        # Also return the query limit-value for ListView
        # This is useful if no limit specified in query, so default applies.
        resultdict[ResultKeys.limit]= limit
        return jsonify(resultdict)


def add_to_apiv0(queryview_class):
    name = queryview_class.view_name
    apiv0.add_url_rule('/' + name,
                       view_func=queryview_class.as_view(name))
    return queryview_class


# @apiv0.route('/')
# def root_redirect():
#     return redirect(url_for(apiv0.name + '.' + 'stream_count'), code=302)

@add_to_apiv0
class AuthoredMonthCount(QueryView):
    """
    Dict: Mapping month -> packet counts per-month.

    Here, 'month' refers to the month of the 'authoring' DateTime,
    i.e. the ``Who.Date`` element of the VOEvent. NB, may be None.


    """
    view_name = 'authored_month_count'

    def get_query(self):
        return query.authored_month_counts_q(db_session)

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


@add_to_apiv0
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


@add_to_apiv0
class IvornList(ListQueryView):
    """
    List: All ivorns matching querystring.
    """
    view_name = 'ivorn'

    def get_query(self):
        return db_session.query(Voevent.ivorn)


@add_to_apiv0
class RoleCount(QueryView):
    """
    Dict: Mapping role -> packet counts per-role.
    """
    view_name = 'role_count'

    def get_query(self):
        return query.role_counts_q(db_session)

    def process_query(self, q):
        return dict(q.all())


@add_to_apiv0
class StreamCount(QueryView):
    """
    Dict: Mapping stream -> packet counts per-stream.
    """
    view_name = 'stream_count'

    def get_query(self):
        return query.stream_counts_q(db_session)

    def process_query(self, q):
        return dict(q.all())


@add_to_apiv0
class StreamRoleCount(QueryView):
    """
    Nested dict: Mapping stream -> role -> packet counts per-role.
    """
    view_name = 'stream_role_count'

    def get_query(self):
        return query.stream_counts_role_breakdown_q(db_session)

    def process_query(self, q):
        return convenience.to_nested_dict(q.all())


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
        abort(404,
              """
              Sorry, IVORN not found.

              Did you remember to
              <a href="http://meyerweb.com/eric/tools/dencoder/">
              URL-encode</a> your IVORN?
              """
              )
