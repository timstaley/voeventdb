from __future__ import absolute_import
from datetime import timedelta

from sqlalchemy import create_engine
import pytest

import voeventparse as vp
from voeventdb.server.database.config import default_admin_db_url, testdb_empty_url
from voeventdb.server.database import db_utils, session_registry, session_factory
from voeventdb.server.database.models import Base, Voevent
import voeventdb.server.tests.fixtures.fake as fake
from voeventdb.server.tests.resources import (swift_bat_grb_655721,
                                              swift_xrt_grb_655721)

from collections import defaultdict


# Would like to use 'session' scoped fixture - i.e. create once for all
# unit-tests.
# But for some reason it still gets called a second time (before destruction of
# first fixture!) and we hit a database contention lock-up.
# For now, we just make it module-level.
#
@pytest.fixture(scope='module')
def empty_db_connection():
    """
    Connect to db, create tables and begin connection-level (outer) transaction.

    Will also create the database first if it does not exist.

    Maybe overkill, but a neat trick, cf:
    http://alextechrants.blogspot.co.uk/2013/08/unit-testing-sqlalchemy-apps.html
    We use a connection-level (non-ORM) transaction that encloses everything
    **including the table creation**.
    This ensures that the models and queries are always in sync for testing.

    Note that the transaction must be explicitly rolled back. An alternative
    approach would be to delete all tables, but presumably that would
    take slightly longer than a rollback (be interesting to check).
    """
    # Could be parameterized, but then it wouldn't make sense as a session-level fixture
    # Unless PyTest is smart enough to maintain fixtures in parallel?
    # test_db_url = getattr(request.module, "test_db_url", testdb_empty_url)
    test_db_url = testdb_empty_url
    if not db_utils.check_database_exists(test_db_url):
        db_utils.create_empty_database(default_admin_db_url, test_db_url.database)
    engine = create_engine(test_db_url)
    connection = engine.connect()
    transaction = connection.begin()
    # Create tables (will be rolled back to clean)
    db_utils.create_tables_and_indexes(connection)
    # Return to test function
    yield connection
    # TearDown
    transaction.rollback()
    connection.close()
    engine.dispose()


@pytest.fixture
def fixture_db_session(empty_db_connection):
    """
    Provide a Session connected to the empty database.

    We use nested transactions to return the database to empty after each test.
    """
    nested_transaction = empty_db_connection.begin_nested()
    session_factory.configure(bind=empty_db_connection)
    session = session_registry()
    yield session
    session_registry.remove()
    nested_transaction.rollback()


class SimpleDbFixture:

    def add_reference(self, packet, ref_ivorn):
        self.n_citations += 1
        # self.cited.add(ref_ivorn)
        self.cite_counts[ref_ivorn] = self.cite_counts[ref_ivorn] + 1
        self.followup_packets.append(packet.attrib['ivorn'])
        vp.add_citations(packet,
                         vp.EventIvorn(
                             ref_ivorn,
                             vp.definitions.cite_types.followup)
                         )


    def __init__(self, fixture_db_session):
        s = fixture_db_session
        packets = [swift_bat_grb_655721]
        packets.extend(fake.heartbeat_packets(role=vp.definitions.roles.test))

        extra_packets = fake.heartbeat_packets(
            start=fake.default_start_dt + timedelta(hours=24),
            role=vp.definitions.roles.utility)

        # Packets referenced by other packets:
        # self.cited = set()
        # Count times ivorn referenced by other packets in db :
        self.cite_counts = defaultdict(int)
        # Packets containing at least one cite entry
        self.followup_packets = []
        # Total number of citations (one packet may have multiple cite entries)
        self.n_citations = 0

        c0 = packets[0].attrib['ivorn']
        c1 = packets[1].attrib['ivorn']
        #One reference in ep0
        self.add_reference(extra_packets[0],  c0)
        #Two references in ep1
        self.add_reference(extra_packets[1],c0)
        self.add_reference(extra_packets[1],c1)
        #
        # #Now cite ep[0], making it both cites / cited_by
        c2 = extra_packets[0].attrib['ivorn']
        self.add_reference(extra_packets[2],c2)

        # Add a citation to an external packet
        self.add_reference(extra_packets[3], swift_xrt_grb_655721.attrib['ivorn'])

        packets.extend(extra_packets)
        self.packet_dict = { pkt.attrib['ivorn'] : pkt for pkt in packets }

        self.insert_packets = packets[:-1]
        self.insert_packets_dumps = [vp.dumps(v) for v in self.insert_packets]
        self.streams = [v.attrib['ivorn'].split('#')[0][6:]
                        for v in self.insert_packets]
        self.stream_set = list(set(self.streams))
        self.roles = [v.attrib['role'] for v in self.insert_packets]
        self.role_set = list(set(self.roles))
        self.remaining_packet = packets[-1]
        # Insert all but the last packet, this gives us a useful counter-example
        s.add_all(
            (Voevent.from_etree(p) for p in self.insert_packets))
        self.n_inserts = len(self.insert_packets)
        self.inserted_ivorns = [p.attrib['ivorn'] for p in self.insert_packets]
        self.absent_ivorn = self.remaining_packet.attrib['ivorn']


@pytest.fixture
def simple_populated_db(fixture_db_session):
    s = fixture_db_session
    packet_info = SimpleDbFixture(s)
    return packet_info
