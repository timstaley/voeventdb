from __future__ import absolute_import
from voeventdb.server.restapi.v1.apierror import InvalidQueryString
from voeventdb.server.restapi.v1.definitions import PaginationKeys

"""
Define the underlying machinery we'll use to implement query filters.
"""

filter_registry = {}


def add_to_filter_registry(cls):
    """
    To be used as a class decorator
    """
    filter_registry[cls.querystring_key] = cls()
    return cls


class QueryFilter(object):
    """
    Provides an interface example for QueryFilter classes to follow, and
    centralises some common code.

    .. Note::
        In earlier iterations, query-filtering was simply performing in one big
        function, which was simpler in terms of using basic language constructs.
        However, it was starting to get very messy, with effectively a
        many-entry 'case' statement, some tricky repeated syntax around
        generating multi-clause filters, etc. Documenting the possible
        query-string filter-keys was also a bit awkward.

        By adopting a 'class-registry' pattern, we require a bit more fussy
        set-up code, but the result is a set of clearly defined filters
        with regular docstrings and self-documenting examples.
        It also allows us to easily check whether a given query-string key is
        valid, and return the relevant HTTP-error if not.
        As a bonus, we can use the registry to create a unit-test matrix via
        pytest's fixture generation, which is neat.
    """
    querystring_key = None
    example_values = None
    simplejoin_tables = None

    def combinator(self, filters):
        """
        Function used to combine multiple filter clauses.

        By default, if a query-key is passed multiple times we just use the
        first value (see below).

        Alternatively, a QueryFilter class may set this equal to SQLAlchemy's
        :py:class:`sqlalchemy,or_` or :py:class:`sqlalchemy.and_` functions.
        """
        return list(filters)[0]

    def filter(self, filter_value):
        return NotImplementedError

    def generate_filter_set(self, args):
        return self.combinator(
            self.filter(filter_value)
            for filter_value in args.getlist(self.querystring_key)
        )

    def apply_filter(self, query, args, pre_joins):
        if self.simplejoin_tables:
            for tbl in self.simplejoin_tables:
                if tbl not in pre_joins:
                    query = query.join(tbl)
                    pre_joins.append(tbl)
        query = query.filter(self.generate_filter_set(args))
        return query


def apply_filters(query, args):
    """
    Apply all QueryFilters, validating the querystring in the process.
    """
    pre_joins = []
    for querystring_key, filter_value in args.items(multi=True):
        if querystring_key in filter_registry:
            cls_inst = filter_registry[querystring_key]
            query = cls_inst.apply_filter(query, args, pre_joins)
        elif querystring_key in PaginationKeys._value_list:
            pass
        else:
            raise InvalidQueryString(querystring_key, filter_value)
    return query



