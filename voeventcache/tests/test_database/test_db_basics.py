from __future__ import absolute_import
from sqlalchemy.exc import IntegrityError
import iso8601
from voeventcache.database.models import Voevent
from voeventcache.database.convenience import ivorn_present
from voeventcache.tests.resources import swift_bat_grb_pos_v2_etree

import pytest


def test_empty_table_present(empty_db_session):
    """
    Make sure the database fixture is initialized as expected.
    """
    s = empty_db_session
    results = s.query(Voevent).all()
    assert results == []


class TestBasicInsert:
    """
    Check that inserting a single VOEvent works as expected.
    """

    @pytest.fixture(autouse=True)
    def insert_single_voevent(self, empty_db_session):
        """Insert a single VOEvent as setup"""
        s = empty_db_session
        assert len(s.query(Voevent).all()) == 0  # sanity check
        s.add(Voevent.from_etree(swift_bat_grb_pos_v2_etree))

    def test_single_voevent_insert(self, empty_db_session):
        """Should have one entry, check its attributes match."""
        s = empty_db_session
        results = s.query(Voevent).all()
        assert len(results) == 1
        assert results[0].ivorn == swift_bat_grb_pos_v2_etree.attrib['ivorn']

    def test_unique_ivorn_constraint(self, empty_db_session):
        s = empty_db_session
        with pytest.raises(IntegrityError):
            # Should throw, breaks unique IVORN constraint:
            s.add(Voevent.from_etree(swift_bat_grb_pos_v2_etree))
            s.flush()


class TestBasicInsertsAndQueries:
    """
    Basic sanity checks. Serve as SQLAlchemy examples as much as anything.
    """

    def test_ivorns(self, simple_db_fixture):
        s, dbinf = simple_db_fixture
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

    def test_convenience_funcs(self, simple_db_fixture):
        s, dbinf = simple_db_fixture
        assert ivorn_present(s, dbinf.inserted_ivorns[0]) == True
        assert ivorn_present(s, dbinf.absent_ivorn) == False

    def test_xml_round_trip(self, simple_db_fixture):
        "Sanity check that XML is not corrupted or prefixed or re-encoded etc"
        s, dbinf = simple_db_fixture
        xml_pkts = [r.xml for r in s.query(Voevent.xml).all()]
        assert xml_pkts == dbinf.insert_packets_dumps

        xml_single = s.query(Voevent.xml).filter(
            Voevent.ivorn == dbinf.insert_packets[0].attrib['ivorn']
        ).scalar()
        assert xml_single == dbinf.insert_packets_dumps[0]

    def test_datetime_comparison(self, simple_db_fixture):
        s, dbinf = simple_db_fixture
        pkt_index = 5
        pkt_timestamp = iso8601.parse_date(
            dbinf.insert_packets[pkt_index].Who.Date.text)
        pkts_before = s.query(Voevent).filter(
            Voevent.author_datetime < pkt_timestamp
        ).count()
        assert pkts_before == pkt_index

        pkts_before_or_same = s.query(Voevent).filter(
            Voevent.author_datetime <= pkt_timestamp
        ).count()
        assert pkts_before_or_same == pkt_index + 1
