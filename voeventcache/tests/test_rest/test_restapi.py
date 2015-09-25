from __future__ import absolute_import
import pytest
from voeventcache.restapi.custom import apiv0
import json
from flask import url_for, request
import iso8601

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
        assert rv.status_code == 200

    def test_api_count(self):
        rv = self.c.get(url_for('apiv0.get_count'))
        rd = json.loads(rv.data)
        assert rv.status_code == 200
        assert rd['count'] == 0


class TestWithSimpleDatabase:
    @pytest.fixture(autouse=True)
    def assign_test_client_and_initdb(self, flask_test_client):
        self.c = flask_test_client  # Purely for brevity

    def test_bare_root(self):
        rv = self.c.get('/')
        assert rv.status_code == 404

    def test_api_root(self):
        rv = self.c.get(apiv0.url_prefix + '/')
        assert rv.status_code == 200

    def test_unfiltered_count(self, simple_populated_db):
        dbinf = simple_populated_db
        rv = self.c.get(url_for('apiv0.get_count'))
        rd = json.loads(rv.data)
        # print rd
        assert rv.status_code == 200
        assert rd['count'] == dbinf.n_inserts
        assert rd['query'] == dict()

    def test_count_w_query(self, simple_populated_db):
        dbinf = simple_populated_db

        pkt_index = 6
        pkt = simple_populated_db.insert_packets[pkt_index]
        authored_until_dt = pkt.Who.Date

        qry_url = url_for('apiv0.get_count',
                          authored_until=authored_until_dt)
        with self.c as c:
            rv = self.c.get(qry_url)
            # print "ARGS:", request.args
        rd = json.loads(rv.data)
        # print rd
        assert rv.status_code == 200
        assert rd['count'] == pkt_index +1 # date bounds are inclusive
        assert rd['query'] == dict(authored_until = authored_until_dt)
