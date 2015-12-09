from __future__ import print_function
import pytest
import voeventdb.server.restapi.inspection_utils as iu
from voeventdb.server.restapi.v1.views import apiv1
from voeventdb.server.restapi.v1.viewbase import OrderValues, PaginationKeys
import logging
logger = logging.getLogger(__name__)

from flask import request, url_for
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