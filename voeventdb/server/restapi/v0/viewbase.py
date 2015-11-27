from __future__ import absolute_import

"""
Base classes used for generating views
"""
from flask.views import View
from flask import (
    jsonify, request, current_app
)

from voeventdb.server.database.models import Voevent
from voeventdb.server.restapi.v0.filter_base import apply_filters
from voeventdb.server.restapi.v0.definitions import (
    OrderValues,
    order_by_string_to_col_map,
    PaginationKeys,
    ResultKeys,
)
from voeventdb.server.restapi.v0.apierror import InvalidQueryString

from sqlalchemy import asc, desc


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
        By default, simply return all columns.
        """
        return query.all()

    def set_ordering(self, query):
        q = query
        order_stringval = request.args.get(PaginationKeys.order, None)
        ordering_func = asc
        if order_stringval:
            if order_stringval not in OrderValues._value_list:
                raise InvalidQueryString(
                    querystring_key=PaginationKeys.order,
                    querystring_value=order_stringval,
                    reason="Not a valid ordering, try one of {}.".format(
                        OrderValues._value_list))

            if order_stringval[-5:] == '_desc':
                ordering_func = desc
                order_stringval = order_stringval[:-5]

        ordering_col = order_by_string_to_col_map[order_stringval]
        q = q.order_by(ordering_func(ordering_col))

        # Usually append id ordering as a tie-breaker, ensures consistency:
        if ordering_col != Voevent.id:
            q = q.order_by(Voevent.id)
        return q

    def dispatch_request(self):
        limit = request.args.get(PaginationKeys.limit, None)
        if not limit:
            limit = current_app.config['DEFAULT_QUERY_LIMIT']

        q = self.get_query()
        q = apply_filters(q, request.args)
        q = self.set_ordering(q)
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
