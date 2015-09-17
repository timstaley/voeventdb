from __future__ import absolute_import
import pytest
from voeventcache.restapi.custom import apiv0
import json
from flask import url_for

#Ensure dbsession gets correctly configured:
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
        