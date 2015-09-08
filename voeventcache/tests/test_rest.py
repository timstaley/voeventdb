from __future__ import absolute_import

from lxml import etree
import unittest

import flask.ext.testing
from voeventcache.database.models import Voevent
from voeventcache.tests.resources import swift_bat_grb_pos_v2_etree
from voeventcache.restapi import restapi

class RestTestBase(flask.ext.testing.TestCase):
    """
    NB too much magic happening under flask extensions to use session rollback;
    just use an in-memory SQLite DB for these tests.
    """
    def create_app(self):
        restapi.app.config['TESTING'] = True
        restapi.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        return restapi.app
    
    def setUp(self):
        #flask-testing cheekily takes care of the 'super' call for us.
        self.db =restapi.db
        self.db.create_all()
        self.prefix = restapi.url_prefix + '/voevent'


    def tearDown(self):
        #flask-testing cheekily takes care of the 'super' call for us.
        self.db.session.remove()
        self.db.drop_all()
        

class TestEmptyResponse(RestTestBase):
    def test_empty_response(self):
        r = self.client.get(self.prefix)
        self.assert200(r)
        self.assertEqual(r.json['num_results'], 0)

@unittest.skip
class TestSingleVoevent(RestTestBase):
    def test_empty_response(self):
        self.db.session.add(Voevent.from_etree(swift_bat_grb_pos_v2_etree))
        self.db.session.commit()
        r = self.client.get(self.prefix)
        self.assert200(r)
        results = r.json['objects']
        self.assertEqual(r.json['num_results'], 1)
        self.assertEqual(r.json['num_results'], len(results))
        self.assertEqual(results[0]['ivorn'],
                         swift_bat_grb_pos_v2_etree.attrib['ivorn'])

