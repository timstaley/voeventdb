from __future__ import absolute_import
from voeventdb.restapi.v0.apierror import InvalidQueryString
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

    def apply_filter(self, query, args):
        return query.filter(self.generate_filter_set(args))

def apply_filters(query, args):
    """
    Apply all QueryFilters.
    """
    for querystring_key,filter_value in args.iteritems(multi=True):
        if querystring_key in filter_registry:
            cls_inst = filter_registry[querystring_key]
            query = cls_inst.apply_filter(query, args)
        elif querystring_key=='limit' or querystring_key=='offset':
            pass
        else:
            raise InvalidQueryString(querystring_key,filter_value)
    return query

def list_querystring_keys():
    return [cls.querystring_key for cls in filter_registry]