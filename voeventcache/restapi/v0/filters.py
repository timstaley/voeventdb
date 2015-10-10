from voeventcache.database.models import Voevent
from .filter_base import add_to_filter_registry, QueryFilter, apply_filters
import iso8601
from sqlalchemy import or_, and_

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
                      '2015-10-09',]
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
                      '2015-10-09',]
    def filter(self, filter_value):
        bound_dt = iso8601.parse_date(filter_value)
        return Voevent.author_datetime <= bound_dt




class QueryKeys:
    authored_since = 'authored_since'
    authored_until = 'authored_until'
    contains = 'contains'
    limit = 'limit'
    offset = 'offset'
    prefix = 'prefix'
    role = 'role'
    stream = 'stream'



#
# def filter_query(q, args):
#     keys = QueryKeys
#     if keys.authored_since in args:
#         q = AuthoredSince().apply_filter(q, args)
#     if keys.authored_until in args:
#         q = AuthoredUntil().apply_filter(q, args)
#     if keys.contains in args:
#         q = q.filter(
#             and_(
#                 Voevent.ivorn.like('%{}%'.format(substr))
#                 for substr in args.getlist(keys.contains)
#             )
#         )
#     if keys.prefix in args:
#         q = q.filter(
#             or_(
#                 Voevent.ivorn.like('{}%'.format(pref))
#                 for pref in args.getlist(keys.prefix)
#             )
#         )
#     if keys.role in args:
#         q = q.filter(Voevent.role == args[keys.role])
#     if keys.stream in args:
#         q = q.filter(Voevent.stream == args[keys.stream])
#     return q