from __future__ import absolute_import
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


from voeventcache.database.models import Base, Voevent
from voeventcache.database import db_utils
from voeventcache.tests.config import (admin_db_url,
                                   testdb_empty_url)
from voeventcache.tests.resources import swift_bat_grb_pos_v2_etree
from voeventcache.tests.fixtures import fake
from voeventcache.tests.fixtures.connection import (
    create_tables_and_begin_transaction,
)
from datetime import datetime, timedelta

# import logging
# logging.basicConfig()


def setUpModule():
    if not db_utils.check_database_exists(testdb_empty_url):
        db_utils.create_database(admin_db_url, testdb_empty_url.database)
    global engine, connection, transaction
    engine, connection, transaction = create_tables_and_begin_transaction(testdb_empty_url)

def tearDownModule():
    ## Roll back the top level transaction and disconnect from the database
    transaction.commit() #Leave the database around for manual inspection
    # transaction.rollback()
    connection.close()
    engine.dispose()

class DBTestCase(unittest.TestCase):
    """
    Run each test-case in a nested transaction and then roll back on teardown.

    This means that each test-case runs on a fresh database as-per setUpModule.
    """
    def setUp(self):
        unittest.TestCase.setUp(self)
        self.__transaction = connection.begin_nested()
        self.session = Session(connection)
    def tearDown(self):
        self.session.close()
        self.__transaction.rollback()


class TestTablesCreatedOK(DBTestCase):
    """Check that querying the empty tables works as expected"""
    def test_empty_table_present(self):
        results = self.session.query(Voevent).all()
        self.assertEqual(results,[])


class TestBasicInsert(DBTestCase):
    """
    Check that inserting a single VOEvent works.
    """
    def setUp(self):
        """Insert a single VOEvent as setup"""
        super(TestBasicInsert, self).setUp()
        #Duplicates 'TestTablesCreatedOK' but serves as a sanity check
        self.assertEqual(len(self.session.query(Voevent).all()), 0)
        self.session.add(Voevent.from_etree(swift_bat_grb_pos_v2_etree))

    def test_single_voevent_insert(self):
        """Should have one entry, check its attributes match."""
        results = self.session.query(Voevent).all()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].ivorn,
                         swift_bat_grb_pos_v2_etree.attrib['ivorn'])
        print
        print results[0]
        print repr(results[0])


    def test_unique_ivorn_constraint(self):
        with self.assertRaises(IntegrityError):
            #Should throw, breaks unique IVORN constraint:
            self.session.add(Voevent.from_etree(swift_bat_grb_pos_v2_etree))
            self.session.flush()

class TestBasicInsertsAndQueries(DBTestCase):
    def test_multiple_voevent_insert(self):
        """
        Insert a few VOEvents
        """
        start = datetime(2015, 1, 1)
        interval = timedelta(minutes=15)
        n_interval = 4*6
        packets = fake.heartbeat_packets(start,
                               start+n_interval*interval,
                               interval)
        self.assertEqual(n_interval,len(packets))
        self.session.add_all((Voevent.from_etree(p) for p in packets))
        inserted = self.session.query(Voevent).all()
        self.assertEqual(len(inserted), len(packets))
        pkt_ivorns = [p.attrib['ivorn'] for p in packets]
        inserted_ivorns = [v.ivorn for v in inserted]
        self.assertEqual(pkt_ivorns, inserted_ivorns)
