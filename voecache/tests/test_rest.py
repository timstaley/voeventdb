from __future__ import absolute_import

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from lxml import etree

import flask.ext.testing

from voecache.models import Base, Voevent
from voecache import db_utils, ingest
from voecache.tests.config import (admin_db_url,
                                   voecache_testdb_url)
from voecache.tests.resources import datapaths
from voecache import restapi

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

class TestSingleVoevent(RestTestBase):
    def test_empty_response(self):
        with open(datapaths.swift_bat_grb_pos_v2) as f:
            ingest.ingest_xml_file(f, self.db.session)
        self.db.session.commit()
        r = self.client.get(self.prefix)
        self.assert200(r)
        results = r.json['objects']
        self.assertEqual(r.json['num_results'], 1)
        self.assertEqual(r.json['num_results'], len(results))
        with open(datapaths.swift_bat_grb_pos_v2) as f:
            root = etree.parse(f).getroot()
        self.assertEqual(results[0]['ivorn'], root.attrib['ivorn'])

