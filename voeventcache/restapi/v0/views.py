from __future__ import absolute_import

from flask import (
    Blueprint, jsonify, abort, request, make_response,
    current_app
)
from flask.views import View

from voeventcache.database import session_registry as db_session
from voeventcache.database.models import Voevent
import voeventcache.database.convenience as convenience
import voeventcache.database.query as query
from voeventcache.restapi.v0.filters import apply_filters

apiv0 = Blueprint('apiv0', __name__,
                  url_prefix='/apiv0')

default_query_limit = 100

class PaginationKeys:
    """
    Use *limit* and *offset* values in your querystring to control slicing,
    i.e. the subset of an ordered list returned in the current query.

    (Only applies to list views, e.g. the IVORN listing endpoint.)

    The keywords are adopted from SQL,
    cf http://www.postgresql.org/docs/9.3/static/queries-limit.html

    Note that if no values are supplied, a default limit value is applied.
    (You can check what it was by inspecting the relevant value in the
    result-dict.)

    The key-strings are exactly what you'd expect, but are documented here
    for completeness:
    """
    limit = 'limit'
    offset = 'offset'

class ResultKeys:
    """
    All endpoints (except the XML-request) return a JSON-encoded dictionary.

    At the top level, the dictionary will contain some or all of the following
    keys. These can be accessed in an autocomplete-friendly fashion to
    aid in building result-handling code,
    for example::

        from voeventcache.restapi.v0 import ResultKeys as rkeys

        print rkeys.querystring
    """
    endpoint = 'endpoint'
    "The endpoint the query was made against."

    limit = 'limit'
    """
    The maximum number of entries returned in a single request
    (Only applies to list-view endpoints.)
    """

    querystring = 'querystring'
    """
    A dictionary displaying the query-string values applied.
    (With urlencode-decoding applied as necessary.)

    Note that each entry returns a list, as a query-key may be applied
    multiple times.
    """

    result = 'result'
    """
    The data returned by your query, either in dictionary
    or list format according to the endpoint.
    """

    url = 'url'
    "The complete URL the query was made against."




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
        q = apply_filters(q, request.args)
        result = self.process_query(q)
        return jsonify(make_response_dict(result))


class ListQueryView(View):
    def get_query(self):
        raise NotImplementedError

    def dispatch_request(self):
        limit = request.args.get(PaginationKeys.limit, None)
        if not limit:
            limit = current_app.config.get('DEFAULT_QUERY_LIMIT',
                                           default_query_limit)
        q = self.get_query()
        q = apply_filters(q, request.args)
        q = q.order_by(Voevent.id)
        q = q.limit(limit)
        q = q.offset(request.args.get(PaginationKeys.offset))
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
    Result:
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
    Result:
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
    Result:
        List: All ivorns matching querystring.
    """
    view_name = 'ivorn'

    def get_query(self):
        return db_session.query(Voevent.ivorn)


@add_to_apiv0
class RoleCount(QueryView):
    """
    Result:
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
    Result:
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
    Result:
        Nested dict: Mapping stream -> role -> packet counts per-stream-and-role.
    """
    view_name = 'stream_role_count'

    def get_query(self):
        return query.stream_counts_role_breakdown_q(db_session)

    def process_query(self, q):
        return convenience.to_nested_dict(q.all())


@apiv0.route('/xml/<path:ivorn>')
def get_xml(ivorn=None):
    """
    Returns the XML packet contents stored for a given IVORN.
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
