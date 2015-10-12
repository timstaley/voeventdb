from __future__ import absolute_import
import pytest
from voeventcache.restapi.v0 import apiv0
from voeventcache.restapi.v0 import ResultKeys
import voeventcache.restapi.v0.views as views
import json
from flask import url_for, request

@pytest.mark.usefixtures('fixture_db_session')
class TestWithEmptyDatabase:
    @pytest.fixture(autouse=True)
    def assign_test_client(self, flask_test_client):
        self.c = flask_test_client  # Purely for brevity

    def test_bare_root(self):
        rv = self.c.get('/')
        assert rv.status_code == 404

    def test_api_root(self):
        rv = self.c.get(apiv0.url_prefix + '/')
        assert rv.status_code == 404

    def test_api_count(self):
        rv = self.c.get(url_for(apiv0.name+'.count'))
        rd = json.loads(rv.data)
        assert rv.status_code == 200
        assert rd[ResultKeys.result] == 0


class TestWithSimpleDatabase:
    @pytest.fixture(autouse=True)
    def assign_test_client_and_initdb(self, flask_test_client):
        self.c = flask_test_client  # Purely for brevity

    def test_unfiltered_count(self, simple_populated_db):
        dbinf = simple_populated_db
        rv = self.c.get(url_for(apiv0.name+'.count'))
        rd = json.loads(rv.data)
        # print rd
        assert rv.status_code == 200
        assert rd[ResultKeys.result] == dbinf.n_inserts
        assert rd[ResultKeys.querystring] == dict()

    def test_count_w_query(self, simple_populated_db):
        dbinf = simple_populated_db
        pkt_index = 6
        pkt = simple_populated_db.insert_packets[pkt_index]
        authored_until_dt = pkt.Who.Date

        qry_url = url_for(apiv0.name+'.count',
                          authored_until=authored_until_dt)
        with self.c as c:
            rv = self.c.get(qry_url)
            # print "ARGS:", request.args
        rd = json.loads(rv.data)
        # print rd
        assert rv.status_code == 200
        assert rd[ResultKeys.result] == pkt_index +1 # date bounds are inclusive
        assert rd[ResultKeys.querystring] == dict(authored_until = [authored_until_dt,])

    def test_ivornlist(self, simple_populated_db):
        dbinf = simple_populated_db
        ivorn_list_url = url_for(apiv0.name+'.'+views.IvornList.view_name)
        rv = self.c.get(ivorn_list_url)
        rd = json.loads(rv.data)
        assert rv.status_code == 200
        assert rd[ResultKeys.result] == dbinf.inserted_ivorns

    def test_consistent_ordering(self, simple_populated_db):
        """
        Check that database results are orded consistently.

        This test needs work - I can't get it to fail on a small test-fixture
        db. Noticed that resultsets were varying when testing against a
        large corpus database with no ordering applied. That has since
        been fixed using::

                order_by(Voevent.id)

        but this test is will not fail even without that line.
        Will leave this here as a sort of 'to do' marker.

        """
        result_sets = []
        for _ in range(10):
            with self.c as c:
                url = url_for(apiv0.name+'.'+views.IvornList.view_name,
                                    limit=3,
                                    contains='TEST')
                # print "URL", url
                rv = self.c.get(url)
                # print "ARGS:", request.args
            rd = json.loads(rv.data)
            rows = rd[ResultKeys.result]
            assert len(rows) == 3
            result_sets.append(rows)
        rs0 = result_sets[0]
        for rs in result_sets:
            assert rs == rs0
