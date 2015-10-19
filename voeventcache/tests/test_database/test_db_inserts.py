from __future__ import absolute_import
from sqlalchemy.exc import IntegrityError

from voeventcache.database.models import Voevent, Cite
from voeventcache.tests.resources import (
    swift_bat_grb_pos_v2_etree,
    swift_bat_grb_655721,
    swift_xrt_grb_655721,
)
import voeventparse as vp

import pytest


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


def test_cite_load_from_etree(fixture_db_session):
    assert len(Cite.from_etree(swift_bat_grb_655721)) == 0
    assert len(Cite.from_etree(swift_xrt_grb_655721)) == 1
    c1 = Cite.from_etree(swift_xrt_grb_655721)[0]
    assert c1.ref_ivorn == swift_bat_grb_655721.attrib['ivorn']
    assert c1.cite_type == vp.definitions.cite_types.followup


class TestCiteInserts:
    """
    Check that citations get inserted correctly
    """

    @pytest.fixture(autouse=True)
    def insert_voevents(self, fixture_db_session):
        """
        Insert two Vovents (GRB, XRT followup) as setup

        (NB XRT packet cites -> BAT packet.)
        """
        s = fixture_db_session
        assert len(s.query(Voevent).all()) == 0  # sanity check
        s.add(Voevent.from_etree(swift_bat_grb_655721))
        s.add(Voevent.from_etree(swift_xrt_grb_655721))
        s.flush()

    def test_citations_loaded(self, fixture_db_session):
        s = fixture_db_session
        # print s.query(Voevent.id, Voevent.ivorn).all()
        # print s.query(Cite).all()
        n_total_cites = s.query(Cite).count()
        assert n_total_cites == 1
        grb_packet_citations = s.query(Voevent). \
            filter(Voevent.ivorn == swift_bat_grb_655721.attrib['ivorn']). \
            one().cites
        xrt_packet_citations = s.query(Voevent). \
            filter(Voevent.ivorn == swift_xrt_grb_655721.attrib['ivorn']). \
            one().cites

        assert len(grb_packet_citations) == 0
        assert len(xrt_packet_citations) == 1
        c0 = xrt_packet_citations[0]
        xrt_voevent_id = s.query(Voevent.id).filter(
            Voevent.ivorn == swift_xrt_grb_655721.attrib['ivorn']
        ).scalar()
        assert c0.voevent_id == xrt_voevent_id
        assert c0.ref_ivorn == swift_bat_grb_655721.attrib['ivorn']

    def test_backref_query(self, fixture_db_session):
        """
        """
        s = fixture_db_session
        backref_voevent = s.query(Cite). \
            filter(Cite.ref_ivorn == swift_bat_grb_655721.attrib['ivorn']) \
            .one().voevent
        xcheck_voevent_id = s.query(Voevent.id). \
            filter(Voevent.ivorn == swift_xrt_grb_655721.attrib['ivorn']). \
            scalar()
        assert backref_voevent.id == xcheck_voevent_id
        assert backref_voevent.ivorn == swift_xrt_grb_655721.attrib['ivorn']
