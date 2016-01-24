from __future__ import absolute_import
from flask import url_for


class InvalidQueryString(Exception):
    code = 400
    description = "Invalid query-string"

    def __init__(self, querystring_key, querystring_value, reason=None):
        Exception.__init__(self)
        self.message = """
            Error parsing query-string - could not parse this section:
            '{0}={1}'\n
            """.format(querystring_key, querystring_value)
        if reason:
            self.message += " - " + reason

class LimitMaxExceeded(Exception):
    code = 413
    description = "Max 'limit' value exceeded"

    def __init__(self, limit_request, limit_max):
        Exception.__init__(self)
        self.message = """
            You requested too many rows ('limit={}').
            The maximum allowed is {}.
            """.format(limit_request, limit_max)


class IvornNotFound(Exception):
    code = 422
    description = 'IVORN not found'

    def __init__(self, ivorn, suggested_ivorn_url=None):
        Exception.__init__(self)

        self.message = """
            Sorry, IVORN: '{0}' not found in the database.
            If your IVORN has been truncated at the '#' character,
            then it probably just needs to be
            <a href="http://meyerweb.com/eric/tools/dencoder/">URL-encoded</a>.
            """.format(ivorn)
        if suggested_ivorn_url:
            self.message += (
                'IVORN listings can be found at <a href="{0}">{0}</a>.'.format(
                suggested_ivorn_url))


class IvornNotSupplied(Exception):
    code = 400
    description = "No IVORN supplied"

    def __init__(self, suggested_ivorn_url=None):
        Exception.__init__(self)
        self.message = """
            Please append an
            <a href="http://meyerweb.com/eric/tools/dencoder/">URL-encoded</a>
            IVORN to the URL.
            """
        if suggested_ivorn_url:
            self.message += (
                'IVORN listings can be found at <a href="{0}">{0}</a>.'.format(
                suggested_ivorn_url))