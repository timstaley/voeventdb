from __future__ import absolute_import
import pytest
from voeventcache.restapi.custom import apiv0
import json
from flask import url_for


@pytest.mark.usefixtures('empty_db_session')
class TestWithEmptyDatabase:
    @pytest.fixture(autouse=True)
    def assign_test_client(self, flask_test_client):
        self.c = flask_test_client         # Purely for brevity

    def test_bare_root(self):
        rv = self.c.get('/')
        assert rv.status_code ==  404

    def test_api_root(self):
        rv = self.c.get(apiv0.url_prefix+'/')
        assert rv.status_code ==  200

    def test_api_count(self):
        rv = self.c.get(url_for('apiv0.get_count'))
        rd = json.loads(rv.data)
        assert rv.status_code ==  200
        assert rd['count'] == 0

@pytest.mark.usefixtures('simple_db_fixture')
class TestWithSimpleDatabase:
    @pytest.fixture(autouse=True)
    def assign_test_client_and_initdb(self, flask_test_client):
        self.c = flask_test_client         # Purely for brevity

    def test_bare_root(self):
        rv = self.c.get('/')
        assert rv.status_code ==  404

    def test_api_root(self):
        rv = self.c.get(apiv0.url_prefix+'/')
        assert rv.status_code ==  200

    def test_api_count(self, simple_db_fixture):
        _, dbinf = simple_db_fixture
        rv = self.c.get(url_for('apiv0.get_count'))
        rd = json.loads(rv.data)
        # print rd
        assert rv.status_code ==  200
        assert rd['count'] == dbinf.n_inserts
