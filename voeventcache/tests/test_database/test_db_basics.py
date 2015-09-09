from __future__ import absolute_import
import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError


from voeventcache.database.models import Base, Voevent
from voeventcache.database.convenience import ivorn_present
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
    # transaction.commit() #Leave the database around for manual inspection
    transaction.rollback()
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
        # print
        # print results[0]


    def test_unique_ivorn_constraint(self):
        with self.assertRaises(IntegrityError):
            #Should throw, breaks unique IVORN constraint:
            self.session.add(Voevent.from_etree(swift_bat_grb_pos_v2_etree))
            self.session.flush()

class TestBasicInsertsAndQueries(DBTestCase):
    """
    Basic sanity checks. Serves as SQLAlchemy examples as much as anything.
    """
    def setUp(self):
        """
        Insert a few VOEvents
        """
        super(TestBasicInsertsAndQueries, self).setUp()
        start = datetime(2015, 1, 1)
        interval = timedelta(minutes=15)
        n_interval = 4*6
        packets = fake.heartbeat_packets(start,
                               start+n_interval*interval,
                               interval)
        self.assertEqual(n_interval,len(packets))
        self.insert_packets = packets[:-1]
        self.remaining_packet = packets[-1]
        #Insert all but the last packet, this gives us a useful counter-example
        self.session.add_all((Voevent.from_etree(p) for p in self.insert_packets))
        self.n_inserts = len(self.insert_packets)
        self.inserted_ivorn = self.insert_packets[0].attrib['ivorn']
        self.absent_ivorn = self.remaining_packet.attrib['ivorn']

        # for r in self.session.query(Voevent).all():
        #     print r

    def test_ivorns(self):
        inserted = self.session.query(Voevent).all()
        self.assertEqual(len(inserted), len(self.insert_packets))
        pkt_ivorns = [p.attrib['ivorn'] for p in self.insert_packets]
        inserted_ivorns = [v.ivorn for v in inserted]
        self.assertEqual(pkt_ivorns, inserted_ivorns)


        n_matches = self.session.query(Voevent).filter(
            Voevent.ivorn==self.inserted_ivorn).count()
        self.assertEqual(n_matches,1)

        n_matches = self.session.query(Voevent).filter(
            Voevent.ivorn==self.absent_ivorn).count()
        self.assertEqual(n_matches,0)

        n_ivorn_prefix_match = self.session.query(Voevent.ivorn).filter(
            Voevent.ivorn.like('ivo://voevent.organization.tld/TEST%')).count()
        self.assertEqual(n_ivorn_prefix_match, self.n_inserts)
        n_ivorn_substr_match = self.session.query(Voevent.ivorn).filter(
            Voevent.ivorn.like('%voevent.organization.tld/TEST%')).count()
        self.assertEqual(n_ivorn_substr_match, self.n_inserts)

    def test_convenience_funcs(self):
        self.assertTrue(ivorn_present(self.session, self.inserted_ivorn))
        self.assertFalse(ivorn_present(self.session, self.absent_ivorn))


