from voeventcache.database.models import Voevent
from .filter_base import add_to_filter_registry, QueryFilter, apply_filters
import iso8601
from sqlalchemy import or_, and_
import urllib


@add_to_filter_registry
class AuthoredSince(QueryFilter):
    """

    Return only VOEvents with a ``Who.Date`` entry dated after the given time.

    (Time-range is inclusive, i.e. ``>=``)

    Date-time strings passed should be in a format parseable by the
    `iso8601.parse_date() <https://bitbucket.org/micktwomey/pyiso8601/#rst-header-parsed-formats>`_
    function (see :py:attr:`example_values`).
    """
    querystring_key = 'authored_since'
    example_values = ['2015-10-09T21:34:19',
                      '2015-10-09', ]

    def filter(self, filter_value):
        bound_dt = iso8601.parse_date(filter_value)
        return Voevent.author_datetime >= bound_dt


@add_to_filter_registry
class AuthoredUntil(QueryFilter):
    """
    Return only VOEvents with a ``Who.Date`` entry dated before the given time.

    (Time-range is inclusive, i.e. ``<=``)

    Date-time strings passed should be in a format parseable by the
    `iso8601.parse_date() <https://bitbucket.org/micktwomey/pyiso8601/#rst-header-parsed-formats>`_
    function (see :py:attr:`example_values`).
    """
    querystring_key = 'authored_until'
    example_values = ['2015-10-09T21:34:19',
                      '2015-10-09', ]

    def filter(self, filter_value):
        bound_dt = iso8601.parse_date(filter_value)
        return Voevent.author_datetime <= bound_dt


@add_to_filter_registry
class IvornContains(QueryFilter):
    """
    Return only VOEvents which have the given substring in their IVORN.
    """
    querystring_key = 'contains'
    example_values = ['BAT_GRB_Pos',
                      'XRT']

    def filter(self, filter_value):
        return Voevent.ivorn.like('%{}%'.format(filter_value))

    def combinator(self, filters):
        return or_(filters)


@add_to_filter_registry
class IvornPrefix(QueryFilter):
    """
    Return only VOEvents where the IVORN begins with the given value.

    Note that the value passed should always be URL-encoded, e.g.::

        urllib.quote_plus('ivo://nasa.gsfc.gcn')


    """
    querystring_key = 'prefix'
    example_values = [
        urllib.quote_plus('ivo://nasa.gsfc.gcn'),
        urllib.quote_plus('ivo://nvo.caltech/voeventnet/catot#1404')
    ]

    def filter(self, filter_value):
        return Voevent.ivorn.like('{}%'.format(filter_value))

    def combinator(self, filters):
        return or_(filters)


@add_to_filter_registry
class RoleEquals(QueryFilter):
    querystring_key = 'role'
    example_values = [
        'observation',
        'utility',
        'test'
    ]

    def filter(self, filter_value):
        return Voevent.role == filter_value

    def combinator(self, filters):
        return or_(filters)


@add_to_filter_registry
class StreamEquals(QueryFilter):
    querystring_key = 'stream'
    example_values = [
        'nasa.gsfc.gcn#SWIFT',
        'nvo.caltech/voeventnet/catot'
    ]
    def filter(self, filter_value):
        return Voevent.stream == filter_value

    def combinator(self, filters):
        return or_(filters)




