from __future__ import absolute_import
import unittest
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from lxml import etree
from voecache.models import Base, Voevent
from voecache import db_utils, ingest
from voecache.tests.config import (admin_db_url,
                                   voecache_testdb_url)
from voecache.tests.resources import datapaths

def setUpModule():
    if not db_utils.check_database_exists(voecache_testdb_url):
        db_utils.create_database(admin_db_url, voecache_testdb_url.database)

    # Maybe overkill, but a useful trick:
    # http://alextechrants.blogspot.co.uk/2013/08/unit-testing-sqlalchemy-apps.html
    # Performs all module tests, including table creation, in transaction
    # to be rolled back:
    global transaction, connection, engine
    engine = create_engine(voecache_testdb_url)
    connection = engine.connect()
    transaction = connection.begin()
    Base.metadata.create_all(connection)

def tearDownModule():
    # Roll back the top level transaction and disconnect from the database
    transaction.rollback()
    connection.close()
    engine.dispose()

class DBTestBase(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.__transaction = connection.begin_nested()
        self.session = Session(connection)
    def tearDown(self):
        self.session.close()
        self.__transaction.rollback()


class TestDeclarativeSchema(DBTestBase):
    def test_table_create(self):
        results = self.session.query(Voevent).all()
        self.assertEqual(results,[])

    def test_voevent_insert(self):
        with open(datapaths.swift_bat_grb_pos_v2) as f:
            ingest.ingest_xml_file(f, self.session)
        results = self.session.query(Voevent).all()
        self.assertEqual(len(results), 1)
        with open(datapaths.swift_bat_grb_pos_v2) as f:
            root = etree.parse(f).getroot()
        self.assertEqual(results[0].ivorn, root.attrib['ivorn'])

