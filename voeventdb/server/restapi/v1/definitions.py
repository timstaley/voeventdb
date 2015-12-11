from copy import deepcopy
from voeventdb.server.database.models import (Voevent,Cite,Coord)

def _list_class_vars(cls, exclude=None):
    """
    Return a dict of all 'regular' (i.e. not prefixed ``_``) class attributes.
    """
    cvars = {k: v for k, v in vars(cls).items()
             if not k.startswith('_')}
    cvars = deepcopy(cvars)
    if exclude is not None:
        for e in exclude:
            cvars.pop(e)
    return cvars


def add_value_list_attribute(cls):
    """
    Adds ``_value_list`` attribute to a class, listing other attribute values.

    Below, I extensively (ab)use classes for namespacing, to define
    various string literals in a way that is both easy to refactor and enables
    autocompletion (given a suitable REPL or IDE).

    This decorator collects the attribute-values of such a class and gathers
    them into a list for easy cross-checking. The list is assigned to the
    class as the ``_value_list`` attribute.
    """
    cls._value_list = _list_class_vars(cls).values()
    return cls


@add_value_list_attribute
class OrderValues:
    """
    Values that may be used in a querystring with the 'order' key.

    E.g. By specifying ``order=author_datetime`` in a querystring,
    results are returned ordered by author_datetime (ascending, i.e. oldest
    first). By default, results are returned in database-id (ascending) order,
    which in effect means that the first results to be loaded into the database
    are returned first.

    Each value has a pairing with a '-' prefix, implying reverse
    (descending) ordering.

    """
    author_datetime = 'author_datetime'
    author_datetime_desc = '-author_datetime'
    """
    Order results by author_datetime (timestamp from the *Who* section).
    Default ('ascending') implies oldest-first.
    """

    id = 'id'
    id_desc = '-id'
    """
    Order results by database-id (assigned as events are added to the database).
    This is the default setting.
    """

    ivorn = 'ivorn'
    ivorn_desc = '-ivorn'
    """
    Order results by ivorn (alphabetically).
    """

order_by_string_to_col_map = {
    OrderValues.author_datetime: Voevent.author_datetime,
    OrderValues.id : Voevent.id,
    OrderValues.ivorn : Voevent.ivorn,
    None : Voevent.id,
}


@add_value_list_attribute
class PaginationKeys:
    """
    These query-keys control the ordering and subset ('page') of results.

    Use *limit* and *offset* values in your querystring to control slicing,
    i.e. the subset of an ordered list returned in the current query.

    (Only applies to list views, e.g. the IVORN listing endpoint.)

    The keywords are adopted from SQL,
    cf http://www.postgresql.org/docs/9.3/static/queries-limit.html

    Note that if no values are supplied, a default limit value is applied.
    (You can still check what it was, by inspecting the relevant value in the
    :ref:`result-dict <returned-content>`.)
    """
    # These hardly need soft-defining, but we include them for completeness.
    limit = 'limit'
    """
    The maximum number of results returned for a single request.
    """
    offset = 'offset'
    """
    The number of rows 'skipped' before returning results for a request.
    """
    order = 'order'
    """
    Controls the ordering of results, before limit and offset are applied.
    Valid values are enumerated by the :class:`.OrderValues` class.
    """


class ResultKeys:
    """
    Most :ref:`endpoints <apiv1_endpoints>` return a JSON-encoded dictionary.
    [#ApartFromXml]_

    At the top level, the dictionary will contain some or all of the following
    keys:

    .. [#ApartFromXml] (The exception is the XML-retrieval endpoint, obviously.)

    .. note::
        The key-strings can be imported and used in autocomplete-friendly
        fashion, for example::

            from voeventdb.server.restapi.v1 import ResultKeys as rkeys
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

    Note that each entry contains a list, as a query-key may be applied
    multiple times.
    """

    result = 'result'
    """
    The data returned by your query, either in dictionary
    or list format according to the endpoint.

    See :ref:`endpoint listings <apiv1_endpoints>` for detail.
    """

    url = 'url'
    "The complete URL the query was made against."
