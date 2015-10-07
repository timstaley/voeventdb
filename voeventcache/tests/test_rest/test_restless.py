from __future__ import absolute_import
import pytest
import json
from flask import url_for
from voeventcache.restapi.restlessapi import restless_voevent_url
from voeventcache.tests.resources import swift_bat_grb_pos_v2_etree
from voeventcache.database.models import Voevent
import pytest

# Ensure dbsession gets correctly configured to empty db:
pytestmark = pytest.mark.usefixtures('fixture_db_session')

pytestmark = pytest.mark.skipif(True,
                    reason="Restless API disabled")


def test_empty_database(flask_test_client):
    c = flask_test_client
    rv = c.get(restless_voevent_url)
    assert rv.status_code == 200
    assert json.loads(rv.data)['num_results'] == 0


def test_single_voevent(fixture_db_session, flask_test_client):
    s = fixture_db_session
    tc = flask_test_client
    s.add(Voevent.from_etree(swift_bat_grb_pos_v2_etree))
    s.commit()
    rv = tc.get(restless_voevent_url)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    rows = data['objects']
    assert data['num_results'] == 1
    assert data['num_results'] == len(rows)
    assert rows[0]['ivorn'] == swift_bat_grb_pos_v2_etree.attrib['ivorn']
    # print rows[0]
