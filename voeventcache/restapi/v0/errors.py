from flask import url_for
class IvornNotFound(Exception):
    code = 422
    description = "IVORN not found"
    def __init__(self, ivorn):
        Exception.__init__(self)
        self.message = """
            Sorry, IVORN:
            "{}"
            not found in the cache.

            If your IVORN has been truncated at the '#' character,
            then it probably just needs to be
            <a href="http://meyerweb.com/eric/tools/dencoder/">
            URL-encoded</a>.

            IVORN listings can be found
            <a href="{}">here</a>.
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
            IVORN listings can be found
            <a href="{}">here</a>.
            """.format(url_for('apiv0.ivorn'))


