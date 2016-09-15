from __future__ import print_function

import logging
import os

import pytest
import voeventdb.server.restapi.inspection_utils as iu
from flask import request, url_for
from voeventdb.server.restapi.v1.viewbase import OrderValues, PaginationKeys
from voeventdb.server.restapi.v1.views import apiv1

logger = logging.getLogger(__name__)

"""
Enumerative unit-test generation. This gets kinda messy.

What we're doing here is fetching a list of all views (endpoints), and a
separate list of all possible filters. Then, for every view, we check that it
runs successfully with every filter, for all of the example values associated
with that filter. If the view is a 'listqueryview', then we further enumerate
over every possible ordering value.

Note: **this does not actually check that results are correct!** Only that
the queries enumerated run successfully, i.e. they create a valid SQLAlchemy
query, and hence evaluate to valid SQL. Even that is a solid win though,
since the queries are being generated algorithmically by combining SQLAlchemy
queries and filters from multiple parts of the codebase.

See the other manually-written unit-test files for separate verifications of key
functionality such as positional queries.

We could take it further and start combining filters in pairs etc, but I figured
this was an acceptable point of trade-off for complexity vs. completeness.

"""

qv_views = [v.view_name for v in iu.queryview_subclasses()]
lqv_views =  [v.view_name for v in iu.listqueryview_subclasses()]
all_views = qv_views + lqv_views

filter_kvs = iu.queryfilter_keys_and_examples_values()

view_filter_value_tuples = []
for vn in all_views:
    for key in filter_kvs:
        for example in filter_kvs[key]:
            view_filter_value_tuples.append((vn, key, example))

import pprint
pp = pprint.PrettyPrinter()
# print("TUPLES")
# pp.pprint(view_filter_value_tuples)

def runtests(flask_test_client,
                 view_name,
                 filter_key,
                 filter_value):
    """
    Define the test code once, use it twice - with empty / populated databases
    """
    url = url_for(apiv1.name+'.'+view_name,
                    **{filter_key:filter_value})
    with flask_test_client as c:
        rv = c.get(url)
        logger.debug("URL: {}".format(request.url))

    assert rv.status_code == 200

    ## Test pagination /ordering works too, if it's a list view:
    if view_name in lqv_views:
        for orderby_value in OrderValues._value_list:
            url = url_for(apiv1.name+'.'+view_name,
                        **{filter_key:filter_value,
                           PaginationKeys.limit: 10,
                           PaginationKeys.offset:5,
                           PaginationKeys.order: orderby_value})
            with flask_test_client as c:
                rv = c.get(url)
                logger.debug("URL: {}".format(request.url))

            assert rv.status_code == 200


# Sometimes get weird database race-condition errors when running these tests
# as part of deployment on a virtualenv. It shouldn't happen, but it doesn't
# really matter, as long as ALL the tests get run on Travis we don't need to
# run these for every deploy, the standard tests should ensure reasonable
# coverage. So, skip if env-variable "VOEVENTDB_DEPLOY" is defined.
# Speeds up installs anyway.
@pytest.mark.skipif(os.getenv("VOEVENTDB_DEPLOY",None) is not None,
                    reason="Deploy mode detected, skipping REST-combo tests.")
@pytest.mark.usefixtures('fixture_db_session')
class TestQueryViewsWithEmptyDatabase:
    @pytest.mark.parametrize("view_name,filter_key,filter_value",
                             view_filter_value_tuples
                             )
    def test_all(self,flask_test_client,
                 view_name,
                 filter_key,
                 filter_value):
        runtests(flask_test_client,
                 view_name,
                 filter_key,
                 filter_value)

@pytest.mark.skipif(os.getenv("VOEVENTDB_DEPLOY",None) is not None,
                    reason="Deploy mode detected, skipping REST-combo tests.")
@pytest.mark.usefixtures('fixture_db_session','simple_populated_db')
class TestQueryViewsWithPopulatedDatabase:
    @pytest.mark.parametrize("view_name,filter_key,filter_value",
                             view_filter_value_tuples
                             )
    def test_all(self,flask_test_client,
                 view_name,
                 filter_key,
                 filter_value):
        runtests(flask_test_client,
                 view_name,
                 filter_key,
                 filter_value)