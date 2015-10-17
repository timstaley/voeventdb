"""
Base classes used for generating views
"""
from flask.views import View
from flask import (
    jsonify, request, current_app
)
from voeventcache.restapi.v0.filters import apply_filters
from voeventcache.database.models import Voevent


class PaginationKeys:
    """
    Use *limit* and *offset* values in your querystring to control slicing,
    i.e. the subset of an ordered list returned in the current query.

    (Only applies to list views, e.g. the IVORN listing endpoint.)

    The keywords are adopted from SQL,
    cf http://www.postgresql.org/docs/9.3/static/queries-limit.html

    Note that if no values are supplied, a default limit value is applied.
    (You can still check what it was, by inspecting the relevant value in the
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
    keys:

    .. note::
        The key-strings can be imported and used in autocomplete-friendly
        fashion, for example::

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

    def process_query(self, query):
        """
        By default, simply return the first column of rows in the list.
        """
        return list(row[0] for row in query)

    def dispatch_request(self):
        limit = request.args.get(PaginationKeys.limit, None)
        if not limit:
            limit = current_app.config['DEFAULT_QUERY_LIMIT']
        q = self.get_query()
        q = apply_filters(q, request.args)
        q = q.order_by(Voevent.id)
        q = q.limit(limit)
        q = q.offset(request.args.get(PaginationKeys.offset))
        result = self.process_query(q)
        resultdict = make_response_dict(result)
        # Also return the query limit-value for ListView
        # This is useful if no limit specified in query, so default applies.
        resultdict[ResultKeys.limit] = limit
        return jsonify(resultdict)


def _add_to_api(queryview_class, api):
    name = queryview_class.view_name
    api.add_url_rule('/' + name,
                       view_func=queryview_class.as_view(name))
    return queryview_class
