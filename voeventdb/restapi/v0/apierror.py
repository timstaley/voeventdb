from __future__ import absolute_import
from flask import url_for

class InvalidQueryString(Exception):
    code = 400
    description = "Invalid query-string"
    def __init__(self, querystring_key, querystring_value):
        Exception.__init__(self)
        self.message = """
            Error parsing query-string - could not parse this section:
            "{0}={1}"
            """.format(querystring_key, querystring_value)

class IvornNotFound(Exception):
    code = 422
    description = "IVORN not found"
    def __init__(self, ivorn):
        Exception.__init__(self)
        self.message = """
            Sorry, IVORN:
            "{0}"
            not found in the cache.

            If your IVORN has been truncated at the '#' character,
            then it probably just needs to be
            <a href="http://meyerweb.com/eric/tools/dencoder/">
            URL-encoded</a>.

            IVORN listings can be found at
            <a href="{1}">{1}</a>.
            """.format(ivorn,url_for('apiv0.ivorn'))


class IvornNotSupplied(Exception):
    code = 400
    description = "No IVORN supplied"
    def __init__(self):
        Exception.__init__(self)
        self.message = """
            Please append an
            <a href="http://meyerweb.com/eric/tools/dencoder/">URL-encoded</a>
            IVORN to the URL.
            IVORN listings can be found at
            <a href="{0}">{0}</a>.
            """.format(url_for('apiv0.ivorn'))
