from __future__ import absolute_import, unicode_literals
from voeventdb.server.database.models import Voevent, Cite, Coord
from voeventdb.server.database.query import coord_cone_search_clause
import voeventdb.server.restapi.v1.apierror as apierror
from voeventdb.server.restapi.v1.filter_base import (
    add_to_filter_registry, QueryFilter)
import iso8601
from sqlalchemy import (or_, and_, exists,
                        )
from sqlalchemy.orm import aliased
import six
if six.PY3:
    from urllib.parse import quote_plus
else:
    from urllib import quote_plus
from flask import json


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
                      '2015-10-09',
                      '2015-10',
                      ]

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
                      '2015-10-09',
                      '2015-10',
                      ]

    def filter(self, filter_value):
        bound_dt = iso8601.parse_date(filter_value)
        return Voevent.author_datetime <= bound_dt


@add_to_filter_registry
class CitedByAny(QueryFilter):
    """
    Return only VOEvents which are cited by another VOEvent in the database.

    Applied via query-strings ``cited=true`` or ``cited=false``
    """
    querystring_key = 'cited'
    example_values = ['true',
                      'false'
                      ]

    def filter(self, filter_value):
        cite2 = aliased(Cite)
        filter_q = exists().where(Voevent.ivorn == cite2.ref_ivorn)
        if filter_value.lower() == 'true':
            return filter_q
        elif filter_value.lower() == 'false':
            return ~filter_q
        else:
            raise apierror.InvalidQueryString(self.querystring_key,
                                              filter_value)


@add_to_filter_registry
class ConeSearch(QueryFilter):
    """
    Return only VOEvents with co-ords in the given cone.

    Cone specified as a 3-element list in JSON format::

        [ra,dec,radius]

    (values in decimal degrees).

    """
    querystring_key = 'cone'
    example_values = [
        '[10,20,5]',
        '[359.9,-30,5]'
    ]
    simplejoin_tables = [Coord, ]

    def filter(self, filter_value):
        try:
            ra, dec, radius = json.loads(filter_value)
        except:
            raise apierror.InvalidQueryString(self.querystring_key,
                                              filter_value)
        if dec < -90.0 or dec > 90.0:
            raise apierror.InvalidQueryString(self.querystring_key,
                                              filter_value,
                                              reason="invalid declination value")
        return coord_cone_search_clause(ra, dec, radius)

@add_to_filter_registry
class CoordsAny(QueryFilter):
    """
    Return only VOEvents which have / do not have associated co-ord positions.

    Applied via query-strings ``coord=true`` or ``coord=false``
    """
    querystring_key = 'coord'
    example_values = ['true',
                      'false'
                      ]

    def filter(self, filter_value):
        filter_q = Voevent.coords.any()
        if filter_value.lower() == 'true':
            return filter_q
        elif filter_value.lower() == 'false':
            return ~filter_q
        else:
            raise apierror.InvalidQueryString(self.querystring_key,
                                              filter_value)

@add_to_filter_registry
class DecGreaterThan(QueryFilter):
    """
    Return VOEvents with position with Dec greater than given value.

    Dec should be specified in decimal degrees.
    """
    querystring_key = 'dec_gt'
    example_values =  ['0',
                       '-45.123'
                       ]
    simplejoin_tables = [Coord, ]
    def filter(self, filter_value):
        try:
            min_dec = float(filter_value)
            if min_dec < -90.0 or min_dec > 90.0:
                raise ValueError
        except:
            raise apierror.InvalidQueryString(self.querystring_key,
                                  filter_value,
                                  reason="invalid declination value")
        return Coord.dec > min_dec


@add_to_filter_registry
class DecLessThan(QueryFilter):
    """
    Return VOEvents with position with Dec less than given value.

    Dec should be specified in decimal degrees.
    """
    querystring_key = 'dec_lt'
    example_values =  ['0',
                       '-45.123'
                       ]
    simplejoin_tables = [Coord, ]
    def filter(self, filter_value):
        try:
            max_dec = float(filter_value)
            if max_dec < -90.0 or max_dec > 90.0:
                raise ValueError
        except:
            raise apierror.InvalidQueryString(self.querystring_key,
                                  filter_value,
                                  reason="invalid declination value")
        return Coord.dec < max_dec


@add_to_filter_registry
class IvornContains(QueryFilter):
    """
    Return only VOEvents which have the given substring in their IVORN.
    """
    querystring_key = 'ivorn_contains'
    example_values = ['BAT_GRB_Pos',
                      'XRT']

    def filter(self, filter_value):
        return Voevent.ivorn.like('%{}%'.format(filter_value))

    def combinator(self, filters):
        """AND"""
        return and_(filters)


@add_to_filter_registry
class IvornPrefix(QueryFilter):
    """
    Return only VOEvents where the IVORN begins with the given value.

    Note that the value passed should be URL-encoded if it contains
    the ``#`` character e.g.::

        quote_plus('ivo://nvo.caltech/voeventnet/catot#1404')


    """
    querystring_key = 'ivorn_prefix'
    example_values = [
        'ivo://nasa.gsfc.gcn',
        quote_plus('ivo://nvo.caltech/voeventnet/catot#1404')
    ]

    def filter(self, filter_value):
        return Voevent.ivorn.like('{}%'.format(filter_value))

    def combinator(self, filters):
        """OR"""
        return or_(filters)


@add_to_filter_registry
class RefAny(QueryFilter):
    """
    Return only VOEvents which make / don't make reference to any other VOEvents.

    Applied via query-strings ``ref_any=true`` or ``ref_any=false``.
    NB 'true'/'false' string-values are case-insensitive, so e.g.
    'true', 'True', 'TRUE', 'tRUe' are all valid.
    """
    querystring_key = 'ref_any'
    example_values = ['true',
                      'True',
                      'false'
                      ]

    def filter(self, filter_value):
        filter_q = Voevent.cites.any()
        if filter_value.lower() == 'true':
            return filter_q
        elif filter_value.lower() == 'false':
            return ~filter_q
        else:
            raise apierror.InvalidQueryString(self.querystring_key,
                                              filter_value)


@add_to_filter_registry
class RefContains(QueryFilter):
    """
    Return VOEvents which reference an IVORN containing the given substring.
    """
    querystring_key = 'ref_contains'
    example_values = [
        quote_plus('BAT_GRB_Pos'),
        quote_plus('GBM_Alert'),
    ]

    def filter(self, filter_value):
        return Voevent.cites.any(
            Cite.ref_ivorn.like('%{}%'.format(filter_value))
        )

    def combinator(self, filters):
        """OR"""
        return or_(filters)


@add_to_filter_registry
class RefExact(QueryFilter):
    """
    Return only VOEvents which contain a ref to the given (url-encoded) IVORN.

    """
    querystring_key = 'ref_exact'
    example_values = [
        quote_plus('ivo://nasa.gsfc.gcn/SWIFT#BAT_GRB_Pos_649113-680'),
        quote_plus(
            'ivo://nasa.gsfc.gcn/Fermi#GBM_Alert_2015-08-10T14:49:38.83_460910982_1-814'),
    ]

    def filter(self, filter_value):
        return Voevent.cites.any(Cite.ref_ivorn == filter_value)

    def combinator(self, filters):
        """OR"""
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
        if filter_value not in self.example_values:
            raise apierror.InvalidQueryString(
                self.querystring_key, filter_value)
        return Voevent.role == filter_value

    def combinator(self, filters):
        """OR"""
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
        """OR"""
        return or_(filters)
