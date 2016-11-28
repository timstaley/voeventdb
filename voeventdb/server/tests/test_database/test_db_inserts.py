from __future__ import absolute_import

import pytest
import voeventdb.server.tests.fixtures.fake as fake
import voeventparse as vp
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from voeventdb.server.database.models import Voevent, Cite, Coord
from voeventdb.server.database.query import coord_cone_search_clause
from voeventdb.server.tests.resources import (
    gaia_16bsg,
    swift_bat_grb_pos_v2_etree,
    swift_bat_grb_655721,
    swift_xrt_grb_655721,
    konus_lc
)


def test_empty_table_present(fixture_db_session):
    """
    Make sure the database fixture is initialized as expected.
    """
    s = fixture_db_session
    results = s.query(Voevent).all()
    assert results == []

    # Check q3c functions loaded
    q3c_version = s.query(func.q3c_version()).all()
    # print q3c_version


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


class TestUtcTimescaleCoordInserts:
    """
    Check that coords get inserted correctly

    These packets use the most common timestamp standard: UTC timescale.
    """

    @pytest.fixture(autouse=True)
    def insert_voevents(self, fixture_db_session):
        """
        Insert two Vovents (mostly blank 'heartbeat' packet, GRB) as setup
        """
        s = fixture_db_session
        assert len(s.query(Voevent).all()) == 0  # sanity check
        s.add(Voevent.from_etree(fake.heartbeat_packets()[0]))
        s.add(Voevent.from_etree(swift_bat_grb_655721))
        s.flush()
        assert len(s.query(Voevent).all()) == 2  # 1 with, 1 without position

    def test_coord_parsing(self):
        positions_parsed = Coord.from_etree(swift_bat_grb_655721)
        assert len(positions_parsed) == 1

    def test_coords_loaded(self, fixture_db_session):
        s = fixture_db_session
        n_total_coords = s.query(Coord).count()
        assert n_total_coords == 1
        grb_packet_coords = s.query(Voevent).filter(
            Voevent.ivorn == swift_bat_grb_655721.attrib['ivorn']
        ).one().coords
        assert len(grb_packet_coords) == 1
        coord0 = grb_packet_coords[0]
        bat_voevent_id = s.query(Voevent.id).filter(
            Voevent.ivorn == swift_bat_grb_655721.attrib['ivorn']
        ).scalar()
        assert coord0.voevent_id == bat_voevent_id
        position = vp.get_event_position(swift_bat_grb_655721)
        assert coord0.ra == position.ra
        assert coord0.dec == position.dec
        assert coord0.error == position.err

    def test_backref_query(self, fixture_db_session):
        """
        """
        s = fixture_db_session
        coord1 = s.query(Coord).one()
        assert coord1.voevent.ivorn == swift_bat_grb_655721.attrib['ivorn']

    def test_spatial_query(self, fixture_db_session):
        s = fixture_db_session
        posn = vp.get_event_position(swift_bat_grb_655721)
        # Cone search centred on the known co-ords should return the row:
        results = s.query(Coord).filter(
            coord_cone_search_clause(posn.ra, posn.dec, 0.5)).all()
        assert len(results) == 1
        # Now bump the cone to the side (so not matching) and check null return
        results = s.query(Coord).filter(
            coord_cone_search_clause(posn.ra, posn.dec + 1.0, 0.5)).all()
        assert len(results) == 0


class TestTdbTimescaleCoordInserts:
    """
    Check that coords get inserted correctly

    GAIA packets use the TDB timescale for their event timestamps.
    """

    def test_insert_tdb_timestamp_voevent(self, fixture_db_session):
        """
        Insert Gaia packet
        """
        s = fixture_db_session
        assert len(s.query(Voevent).all()) == 0  # sanity check
        s.add(Voevent.from_etree(gaia_16bsg))
        s.flush()
        assert len(s.query(Voevent).all()) == 1
        positions_parsed = Coord.from_etree(gaia_16bsg)
        assert len(positions_parsed) == 1
        gaia_posn = positions_parsed[0]
        assert gaia_posn.time is not None


def test_bad_coord_rejection():
    v = Voevent.from_etree(konus_lc)
    assert v.coords == []
