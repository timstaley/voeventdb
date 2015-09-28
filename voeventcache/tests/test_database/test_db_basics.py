from __future__ import absolute_import
from sqlalchemy.exc import IntegrityError
import iso8601
from voeventcache.database.models import Voevent
from voeventcache.database.convenience import ivorn_present, safe_insert_voevent
import voeventcache.database.convenience as convenience
from voeventcache.tests.resources import swift_bat_grb_pos_v2_etree
import voeventcache.database.query as qry
import copy

import pytest
import logging


def test_empty_table_present(fixture_db_session):
    """
    Make sure the database fixture is initialized as expected.
    """
    s = fixture_db_session
    results = s.query(Voevent).all()
    assert results == []


class TestBasicInsert:
    """
    Check that inserting a single VOEvent works as expected.
    """

    @pytest.fixture(autouse=True)
    def insert_single_voevent(self, fixture_db_session):
        """Insert a single VOEvent as setup"""
        s = fixture_db_session
        assert len(s.query(Voevent).all()) == 0  # sanity check
        s.add(Voevent.from_etree(swift_bat_grb_pos_v2_etree))

    def test_single_voevent_insert(self, fixture_db_session):
        """Should have one entry, check its attributes match."""
        s = fixture_db_session
        results = s.query(Voevent).all()
        assert len(results) == 1
        assert results[0].ivorn == swift_bat_grb_pos_v2_etree.attrib['ivorn']

    def test_unique_ivorn_constraint(self, fixture_db_session):
        s = fixture_db_session
        with pytest.raises(IntegrityError):
            # Should throw, breaks unique IVORN constraint:
            s.add(Voevent.from_etree(swift_bat_grb_pos_v2_etree))
            s.flush()


class TestBasicInsertsAndQueries:
    """
    Basic sanity checks. Serve as SQLAlchemy examples as much as anything.
    """

    def test_ivorns(self, fixture_db_session, simple_populated_db):
        s = fixture_db_session
        dbinf = simple_populated_db
        inserted = s.query(Voevent).all()
        assert len(inserted) == len(dbinf.insert_packets)
        pkt_ivorns = [p.attrib['ivorn'] for p in dbinf.insert_packets]
        inserted_ivorns = [v.ivorn for v in inserted]
        assert pkt_ivorns == inserted_ivorns

        # Cross-match against a known-inserted IVORN
        assert 1 == s.query(Voevent).filter(
            Voevent.ivorn == dbinf.inserted_ivorns[0]).count()

        # And against a known-absent IVORN
        assert 0 == s.query(Voevent).filter(
            Voevent.ivorn == dbinf.absent_ivorn).count()

        # Test 'IVORN.startswith(prefix)' equivalent
        assert dbinf.n_inserts == s.query(Voevent.ivorn).filter(
            Voevent.ivorn.like('ivo://voevent.organization.tld/TEST%')).count()

        # Test 'substr in IVORN' equivalent
        assert dbinf.n_inserts == s.query(Voevent.ivorn).filter(
            Voevent.ivorn.like('%voevent.organization.tld/TEST%')).count()

    def test_xml_round_trip(self, fixture_db_session, simple_populated_db):
        "Sanity check that XML is not corrupted or prefixed or re-encoded etc"
        s = fixture_db_session
        dbinf = simple_populated_db
        xml_pkts = [r.xml for r in s.query(Voevent.xml).all()]
        assert xml_pkts == dbinf.insert_packets_dumps

        xml_single = s.query(Voevent.xml).filter(
            Voevent.ivorn == dbinf.insert_packets[0].attrib['ivorn']
        ).scalar()
        assert xml_single == dbinf.insert_packets_dumps[0]

    def test_datetime_comparison(self, fixture_db_session, simple_populated_db):
        s = fixture_db_session
        dbinf = simple_populated_db
        pkt_index = 5
        threshold_timestamp = iso8601.parse_date(
            dbinf.insert_packets[pkt_index].Who.Date.text)
        pkts_before_calc = 0
        pkts_before_or_same_calc = 0
        for v in simple_populated_db.insert_packets:
            whodate = iso8601.parse_date(v.Who.Date.text)
            if whodate < threshold_timestamp:
                pkts_before_calc += 1
            if whodate <= threshold_timestamp:
                pkts_before_or_same_calc += 1

        pkts_before_db = s.query(Voevent).filter(
            Voevent.author_datetime < threshold_timestamp
        ).count()
        assert pkts_before_calc == pkts_before_db

        pkts_before_or_same_db = s.query(Voevent).filter(
            Voevent.author_datetime <= threshold_timestamp
        ).count()
        assert pkts_before_or_same_calc == pkts_before_or_same_db

class TestConvenienceFuncs:
    def test_ivorn_present(self, fixture_db_session, simple_populated_db):
        s = fixture_db_session
        dbinf = simple_populated_db
        assert ivorn_present(s, dbinf.inserted_ivorns[0]) == True
        assert ivorn_present(s, dbinf.absent_ivorn) == False

    def test_safe_insert(self, fixture_db_session, simple_populated_db,
                         caplog
                         ):

        s = fixture_db_session
        dbinf = simple_populated_db
        nlogs = len(caplog.records())
        with caplog.atLevel(logging.WARNING):
            safe_insert_voevent(s, dbinf.insert_packets[0])
        assert len(caplog.records()) == nlogs + 1
        assert caplog.records()[-1].levelname == 'WARNING'

        bad_packet = copy.copy(dbinf.insert_packets[0])
        bad_packet.Who.AuthorIVORN='ivo://foo.bar'
        with pytest.raises(ValueError):
            safe_insert_voevent(s, bad_packet)

    def test_stream_count(self, fixture_db_session, simple_populated_db):
        results = convenience.stream_counts(fixture_db_session).all()
        assert len(results) == 1
        r0 = results[0]
        assert r0.streamid == simple_populated_db.streams[0]
        assert r0.streamcount == simple_populated_db.n_inserts

    def test_stream_count_with_role(self, fixture_db_session, simple_populated_db):
        """
        Assumes fake packets all belong to one stream.
        """
        roles_insert = set((v.attrib['role'] for v in simple_populated_db.insert_packets))
        results = convenience.stream_counts_role_breakdown(fixture_db_session).all()
        assert len(results) == len(roles_insert)
        for r in results:
            role = r.role
            matching_pkts = [v for v in simple_populated_db.insert_packets
                             if v.attrib['role']==role ]
            assert r.streamid == simple_populated_db.streams[0]
            assert r.streamcount == len(matching_pkts)