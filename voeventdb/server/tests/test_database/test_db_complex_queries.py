from __future__ import absolute_import, print_function

from voeventdb.server.database.convenience import (
    ivorn_present,
    ivorn_prefix_present,
    safe_insert_voevent,
)
import voeventdb.server.database.convenience as convenience
import voeventdb.server.database.query as query

import copy

import pytest
import logging


class TestConvenienceFuncs:
    def test_ivorn_present(self, fixture_db_session, simple_populated_db):
        s = fixture_db_session
        dbinf = simple_populated_db
        assert ivorn_present(s, dbinf.inserted_ivorns[0]) == True
        assert ivorn_present(s, dbinf.absent_ivorn) == False

    def test_ivorn_prefix_present(self, fixture_db_session, simple_populated_db):
        s = fixture_db_session
        dbinf = simple_populated_db
        assert ivorn_prefix_present(s, dbinf.inserted_ivorns[0]) == True
        assert ivorn_prefix_present(s, dbinf.inserted_ivorns[0][:-3]) == True
        assert ivorn_prefix_present(s, dbinf.absent_ivorn) == False

    def test_safe_insert(self, fixture_db_session, simple_populated_db,
                         caplog
                         ):
        s = fixture_db_session
        dbinf = simple_populated_db
        nlogs = len(caplog.records)
        with caplog.at_level(logging.WARNING):
            safe_insert_voevent(s, dbinf.insert_packets[0])
        assert len(caplog.records) == nlogs + 1
        assert caplog.records[-1].levelname == 'WARNING'

        bad_packet = copy.copy(dbinf.insert_packets[0])
        bad_packet.Who.AuthorIVORN = 'ivo://foo.bar'
        with pytest.raises(ValueError):
            safe_insert_voevent(s, bad_packet)

    def test_stream_count(self, fixture_db_session, simple_populated_db):
        sc = dict(query.stream_counts_q(fixture_db_session).all())
        assert len(sc) == len(simple_populated_db.stream_set)

        assert sum(sc.values()) == simple_populated_db.n_inserts

    def test_stream_count_with_role(self, fixture_db_session,
                                    simple_populated_db):
        """
        Assumes fake packets all belong to one stream.
        """
        roles_insert = set(
            (v.attrib['role'] for v in simple_populated_db.insert_packets))
        q = query.stream_counts_role_breakdown_q(fixture_db_session)
        rb = convenience.to_nested_dict(q.all())
        assert len(rb) == len(simple_populated_db.stream_set)
        n_total_ivorn = 0
        for stream_breakdown in rb.values():
            for role_count in stream_breakdown.values():
                n_total_ivorn +=role_count
        assert n_total_ivorn == simple_populated_db.n_inserts



class TestCitationQueries:
    def test_ref_counts(self, fixture_db_session, simple_populated_db):
        s = fixture_db_session
        dbinf = simple_populated_db
        q = query.ivorn_cites_to_others_count_q(s)
        ref_counts = dict(q.all())
        total_refs = sum(ref_counts.values())
        assert dbinf.n_citations == total_refs
        for ivorn in ref_counts:
            if ivorn in dbinf.followup_packets:
                assert ref_counts[ivorn] != 0
            else:
                assert ref_counts[ivorn] == 0
