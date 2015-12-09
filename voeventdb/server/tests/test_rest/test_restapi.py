from __future__ import absolute_import
import pytest
from voeventdb.server.database.models import Cite
from voeventdb.server.restapi.v1.views import apiv1
from voeventdb.server.restapi.v1.definitions import (
    OrderValues,
    PaginationKeys,
    ResultKeys,
)
import voeventdb.server.restapi.v1.views as views
import voeventdb.server.restapi.v1.filters as filters
import json
import urllib
from flask import url_for
import iso8601



@pytest.mark.usefixtures('fixture_db_session')
class TestWithEmptyDatabase:
    @pytest.fixture(autouse=True)
    def assign_test_client(self, flask_test_client):
        self.c = flask_test_client  # Purely for brevity

    def test_bare_root(self):
        rv = self.c.get('/')
        assert rv.status_code == 404

    def test_api_root(self):
        rv = self.c.get(apiv1.url_prefix + '/')
        assert rv.status_code == 200

    def test_api_count(self):
        rv = self.c.get(url_for(apiv1.name + '.' + views.Count.view_name))
        rd = json.loads(rv.data)
        assert rv.status_code == 200
        assert rv.mimetype == 'application/json'
        assert rd[ResultKeys.result] == 0

    def test_no_ivorn(self):
        rv = self.c.get(url_for(apiv1.name + '.xml_view'))
        assert rv.status_code == 400

    def test_ivorn_not_found(self):
        rv = self.c.get(url_for(apiv1.name + '.xml_view') +
                        urllib.quote_plus('foobar_invalid_ivorn'))
        assert rv.status_code == 422


class TestWithSimpleDatabase:
    @pytest.fixture(autouse=True)
    def assign_test_client_and_initdb(self, flask_test_client):
        self.c = flask_test_client  # Purely for brevity

    def test_unfiltered_count(self, simple_populated_db):
        dbinf = simple_populated_db
        rv = self.c.get(url_for(apiv1.name + '.' + views.Count.view_name))
        rd = json.loads(rv.data)
        # print rd
        assert rv.status_code == 200
        assert rd[ResultKeys.result] == dbinf.n_inserts
        assert rd[ResultKeys.querystring] == dict()

    def test_count_w_query(self, simple_populated_db):
        dbinf = simple_populated_db
        pkt_index = 6
        pkt = simple_populated_db.insert_packets[pkt_index]
        authored_until_dt = iso8601.parse_date(pkt.Who.Date.text)
        qualifying_packets = [
            p for p in dbinf.insert_packets
            if iso8601.parse_date(p.Who.Date.text) <= authored_until_dt]

        qry_url = url_for(apiv1.name + '.' + views.Count.view_name,
                          authored_until=authored_until_dt.isoformat())
        with self.c as c:
            rv = self.c.get(qry_url)
            # print "ARGS:", request.args

        assert rv.status_code == 200
        rd = json.loads(rv.data)
        assert len(qualifying_packets)
        assert rd[ResultKeys.result] == len(qualifying_packets)  # date bounds are inclusive
        assert rd[ResultKeys.querystring] == dict(
            authored_until=[authored_until_dt.isoformat(), ])

    def test_count_w_multiquery(self, simple_populated_db):
        dbinf = simple_populated_db
        qry_url = (
            url_for(apiv1.name + '.' + views.Count.view_name)
            + '?' +
            urllib.urlencode((('role', 'test'),
                              ('role', 'utility'),
                              ('role', 'observation')))
        )
        rv = self.c.get(qry_url)
        assert rv.status_code == 200
        rd = json.loads(rv.data)
        assert rd[ResultKeys.result] == dbinf.n_inserts

    def test_ivornlist(self, simple_populated_db):
        dbinf = simple_populated_db
        ivorn_list_url = url_for(apiv1.name + '.' + views.IvornList.view_name)
        rv = self.c.get(ivorn_list_url)
        assert rv.status_code == 200
        rd = json.loads(rv.data)
        assert rd[ResultKeys.result] == dbinf.inserted_ivorns

    def test_consistent_ordering(self, simple_populated_db):
        """
        Check that database results are orded consistently.

        This test needs work - I can't get it to fail on a small test-fixture
        db. Noticed that resultsets were varying when testing against a
        large corpus database with no ordering applied. That has since
        been fixed using::

                order_by(Voevent.id)

        but this test will not fail even without that line.
        Will leave this here as a sort of 'to do' marker.

        """
        result_sets = []
        for _ in range(10):
            with self.c as c:
                url = url_for(apiv1.name + '.' + views.IvornList.view_name,
                              limit=3,
                              ivorn_contains='TEST')
                # print "URL", url
                rv = self.c.get(url)
                # print "ARGS:", request.args
            rd = json.loads(rv.data)
            rows = rd[ResultKeys.result]
            assert len(rows) == 3
            result_sets.append(rows)
        rs0 = result_sets[0]
        for rs in result_sets:
            assert rs == rs0

    def test_reference_counts(self, simple_populated_db):
        """
        Test reference counts are as expected.

        NB we check that 'order by id' works as expected (Voevent.id,
        not cite.id!)
        """
        with self.c as c:
            url = url_for(
                apiv1.name + '.' + views.IvornReferenceCount.view_name,
                **{PaginationKeys.order: OrderValues.id}
            )
            rv = self.c.get(url)
        assert rv.status_code == 200
        rd = json.loads(rv.data)
        ivorn_refcounts = rd[ResultKeys.result]
        counts = zip(*ivorn_refcounts)[1]
        assert sum(counts) == simple_populated_db.n_citations
        for ivorn, refcount in ivorn_refcounts:
            assert bool(refcount) == (
                ivorn in simple_populated_db.followup_packets)

    def test_cited_counts(self, simple_populated_db):
        dbinf = simple_populated_db

        n_internal_citations = 0
        for ivorn, count in dbinf.cite_counts.iteritems():
            if ivorn in dbinf.inserted_ivorns:
                n_internal_citations += count

        with self.c as c:
            url = url_for(apiv1.name + '.' + views.IvornCitedCount.view_name)
            rv = self.c.get(url)
        assert rv.status_code == 200
        rd = json.loads(rv.data)
        ivorn_citecounts = rd[ResultKeys.result]
        counts = zip(*ivorn_citecounts)[1]
        assert sum(counts) == n_internal_citations
        for ivorn, citecount in ivorn_citecounts:
            assert citecount == dbinf.cite_counts[ivorn]

    def test_xml_retrieval(self, simple_populated_db):
        url = url_for(apiv1.name + '.xml_view')
        url += urllib.quote_plus(simple_populated_db.absent_ivorn)
        rv = self.c.get(url)
        assert rv.status_code == 422

        present_ivorn = simple_populated_db.inserted_ivorns[0]
        present_ivorn_xml_content = simple_populated_db.insert_packets_dumps[0]
        url = url_for(apiv1.name + '.xml_view')
        url += urllib.quote_plus(present_ivorn)
        rv = self.c.get(url)
        assert rv.status_code == 200
        assert rv.mimetype == 'text/xml'
        assert rv.data == present_ivorn_xml_content

    def test_synopsis_view(self, simple_populated_db):
        # Null case, ivorn not in DB:
        ep_url = url_for(apiv1.name + '.synopsis_view')
        url = ep_url + urllib.quote_plus(simple_populated_db.absent_ivorn)
        rv = self.c.get(url)
        assert rv.status_code == 422

        # Positive case, ivorn which has references:
        ivorn_w_refs = list(simple_populated_db.followup_packets)[0]
        url = ep_url + urllib.quote_plus(ivorn_w_refs)
        rv = self.c.get(url)
        assert rv.status_code == 200
        rd = json.loads(rv.data)
        full = rd[ResultKeys.result]
        etree = simple_populated_db.packet_dict[ivorn_w_refs]
        assert len(full['refs']) == len(Cite.from_etree(etree))

        # Negative case, IVORN present but packet contains no references
        all_ivorns = set(simple_populated_db.packet_dict.keys())
        ivorns_wo_refs = list(
            all_ivorns - set(simple_populated_db.followup_packets))
        ivorn = ivorns_wo_refs[0]
        url = ep_url + urllib.quote_plus(ivorn)
        rv = self.c.get(url)
        assert rv.status_code == 200
        rd = json.loads(rv.data)
        full = rd[ResultKeys.result]
        assert len(full['refs']) == 0

        # Find packet which cites a SWIFT GRB, check URLs looked up correctly:
        ref_string = 'BAT_GRB'
        url = url_for(apiv1.name + '.' + views.IvornList.view_name,
                      **{filters.RefContains.querystring_key: ref_string}
                      )
        rv = self.c.get(url)
        ref_lists = [ Cite.from_etree(p)
                    for p in simple_populated_db.insert_packets
                    if Cite.from_etree(p)]
        matches = []
        for rl in ref_lists:
            for r in rl:
                if ref_string in r.ref_ivorn:
                    matches.append(r)
                    continue
        matched_via_restapi = json.loads(rv.data)[ResultKeys.result]
        assert len(matched_via_restapi) == len(matches)
        url = ep_url + urllib.quote_plus(matched_via_restapi[0])
        rv = self.c.get(url)
        rd = json.loads(rv.data)[ResultKeys.result]
        # When referencing a Swift alert, we should annotate for two urls,
        # GCN.gsfc.nasa.gov / www.swift.ac.uk
        assert len(rd['relevant_urls']) == 2



        # def test_ref_view(self, simple_populated_db):
