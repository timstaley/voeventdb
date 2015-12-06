from __future__ import absolute_import
import iso8601
from voeventdb.server.database.models import Voevent
import pytest


class TestBasicInsertsAndQueries:
    """
    Basic sanity checks. Serve as SQLAlchemy examples as much as anything.
    """

    def test_ivorns(self, fixture_db_session, simple_populated_db):
        s = fixture_db_session
        dbinf = simple_populated_db
        inserted = s.query(Voevent).all()
        assert len(inserted) == len(dbinf.insert_packets)
        pkt_ivorns = [i.attrib['ivorn'] for i in dbinf.insert_packets]
        inserted_ivorns = [v.ivorn for v in inserted]
        assert pkt_ivorns == inserted_ivorns

        # Cross-match against a known-inserted IVORN
        assert 1 == s.query(Voevent).filter(
            Voevent.ivorn == dbinf.inserted_ivorns[0]).count()

        # And against a known-absent IVORN
        assert 0 == s.query(Voevent).filter(
            Voevent.ivorn == dbinf.absent_ivorn).count()

        # Test 'IVORN.startswith(prefix)' equivalent
        prefix_str = "ivo://voevent.organization.tld/TEST"
        n_matches = len([i for i in dbinf.inserted_ivorns
                         if i.startswith(prefix_str)])
        assert n_matches == s.query(Voevent.ivorn).filter(
            Voevent.ivorn.like('{}%'.format(prefix_str))).count()

        # Test 'substr in IVORN' equivalent
        substr = "voevent.organization.tld/TEST"
        n_matches = len([i for i in dbinf.inserted_ivorns
                         if substr in i])
        assert n_matches == s.query(Voevent.ivorn).filter(
            Voevent.ivorn.like('%{}%'.format(substr))).count()

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
