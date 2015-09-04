from __future__ import absolute_import
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import DatabaseError, IntegrityError
from lxml import etree

from voeventcache.database.models import Base, Voevent
from voeventcache.database import db_utils
from voeventcache.tests.config import (admin_db_url,
                                   voecache_testdb_url)
from voeventcache.tests.resources import swift_bat_grb_pos_v2_etree

# import logging
# logging.basicConfig()


def setUpModule():
    if not db_utils.check_database_exists(voecache_testdb_url):
        db_utils.create_database(admin_db_url, voecache_testdb_url.database)

    # Maybe overkill, but a neat trick:
    # http://alextechrants.blogspot.co.uk/2013/08/unit-testing-sqlalchemy-apps.html
    # Performs all module tests, including table creation, in transaction
    # to be rolled back:
    global transaction, connection, engine
    engine = create_engine(voecache_testdb_url,
                           # echo=True
                           )
    connection = engine.connect()
    transaction = connection.begin()
    Base.metadata.create_all(connection)

def tearDownModule():
    # Roll back the top level transaction and disconnect from the database

    # transaction.commit() #Leave the database around for manual inspection
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

    def test_single_voevent_insert(self):
        """
        Do the most basic thing possible -
        Check that inserting a single VOEvent works.

        Then, check that attempting to insert the same again is rejected.
        """
        results = self.session.query(Voevent).all()
        self.assertEqual(len(results), 0)

        self.session.add(Voevent.from_etree(swift_bat_grb_pos_v2_etree))
        results = self.session.query(Voevent).all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].ivorn,
                         swift_bat_grb_pos_v2_etree.attrib['ivorn'])


        # This is going to break! Exceptions need rollbacks.
        # So, Begin a (sub-)nested transaction that we can rollback:
        self.session.begin_nested()
        with self.assertRaises(IntegrityError) as insertion_error:
            #Should throw, breaks unique IVORN constraint:
            self.session.add(Voevent.from_etree(swift_bat_grb_pos_v2_etree))
            self.session.flush()
        self.session.rollback()

        results = self.session.query(Voevent).all()
        self.assertEqual(len(results), 1)

    def test_multiple_voevent_insert(self):
        """
        Insert a few VOEvents
        """
