from __future__ import absolute_import
import pytest
from voeventdb.server.database.models import Voevent, Cite
from voeventdb.server.restapi.v1.views import apiv1
from voeventdb.server.restapi.v1.definitions import (
    OrderValues,
    PaginationKeys,
    ResultKeys,
)
import voeventdb.server.restapi.v1.views as views
import voeventdb.server.restapi.v1.filters as filters
from voeventdb.server.tests.fixtures.fake import heartbeat_packets
import voeventdb.server.restapi.default_config as rest_app_config
import voeventparse as vp
import json
import six

if six.PY3:
    from urllib.parse import quote_plus, urlencode
else:
    from urllib import quote_plus, urlencode
from flask import url_for, request
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
        rd = json.loads(rv.data.decode())
        assert rv.status_code == 200
        assert rv.mimetype == 'application/json'
        assert rd[ResultKeys.result] == 0

    def test_no_ivorn(self):
        rv = self.c.get(url_for(apiv1.name + '.packet_xml'))
        assert rv.status_code == 400

    def test_ivorn_not_found(self):
        rv = self.c.get(url_for(apiv1.name + '.packet_xml') +
                        quote_plus('foobar_invalid_ivorn'))
        assert rv.status_code == 422


class TestWithSimpleDatabase:
    @pytest.fixture(autouse=True)
    def assign_test_client_and_initdb(self, flask_test_client):
        self.c = flask_test_client  # Purely for brevity

    def test_unfiltered_count(self, simple_populated_db):
        dbinf = simple_populated_db
        rv = self.c.get(url_for(apiv1.name + '.' + views.Count.view_name))
        rd = json.loads(rv.data.decode())
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
        rd = json.loads(rv.data.decode())
        assert len(qualifying_packets)
        # date bounds are inclusive:
        assert rd[ResultKeys.result] == len(qualifying_packets)
        assert rd[ResultKeys.querystring] == dict(
            authored_until=[authored_until_dt.isoformat(), ])

    def test_count_w_multiquery(self, simple_populated_db):
        dbinf = simple_populated_db
        qry_url = (
            url_for(apiv1.name + '.' + views.Count.view_name)
            + '?' +
            urlencode((('role', 'test'),
                       ('role', 'utility'),
                       ('role', 'observation')))
        )
        rv = self.c.get(qry_url)
        assert rv.status_code == 200
        rd = json.loads(rv.data.decode())
        assert rd[ResultKeys.result] == dbinf.n_inserts

    def test_ivornlist(self, simple_populated_db):
        dbinf = simple_populated_db
        ivorn_list_url = url_for(apiv1.name + '.' + views.ListIvorn.view_name)
        rv = self.c.get(ivorn_list_url)
        assert rv.status_code == 200
        rd = json.loads(rv.data.decode())
        assert rd[ResultKeys.result] == dbinf.inserted_ivorns

    def test_row_limit(self, simple_populated_db):
        maxlimit = rest_app_config.MAX_QUERY_LIMIT
        # Limit at max should be OK:
        ivorn_list_url = url_for(apiv1.name + '.' + views.ListIvorn.view_name,
                                 **{PaginationKeys.limit: maxlimit})
        rv = self.c.get(ivorn_list_url)
        assert rv.status_code == 200
        # Limit at max+1 should fail, 413:
        ivorn_list_url = url_for(apiv1.name + '.' + views.ListIvorn.view_name,
                                 **{PaginationKeys.limit: maxlimit + 1})
        rv = self.c.get(ivorn_list_url)
        assert rv.status_code == 413

        # Non-integer values should return a 400
        ivorn_list_url = url_for(apiv1.name + '.' + views.ListIvorn.view_name,
                                 **{PaginationKeys.limit: 'foobar'})
        rv = self.c.get(ivorn_list_url)
        assert rv.status_code == 400
        ivorn_list_url = url_for(apiv1.name + '.' + views.ListIvorn.view_name,
                                 **{PaginationKeys.limit: '1.23'})
        rv = self.c.get(ivorn_list_url)
        assert rv.status_code == 400

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
                url = url_for(apiv1.name + '.' + views.ListIvorn.view_name,
                              limit=3,
                              ivorn_contains='TEST')
                # print "URL", url
                rv = self.c.get(url)
                # print "ARGS:", request.args
            rd = json.loads(rv.data.decode())
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
                apiv1.name + '.' + views.ListIvornReferenceCount.view_name,
                **{PaginationKeys.order: OrderValues.id}
            )
            rv = self.c.get(url)
        assert rv.status_code == 200
        rd = json.loads(rv.data.decode())
        ivorn_refcounts = rd[ResultKeys.result]
        counts = list(zip(*ivorn_refcounts))[1]
        assert sum(counts) == simple_populated_db.n_citations
        for ivorn, refcount in ivorn_refcounts:
            assert bool(refcount) == (
                ivorn in simple_populated_db.followup_packets)

    def test_cited_counts(self, simple_populated_db):
        dbinf = simple_populated_db

        n_internal_citations = 0
        for ivorn, count in dbinf.cite_counts.items():
            if ivorn in dbinf.inserted_ivorns:
                n_internal_citations += count

        with self.c as c:
            url = url_for(
                apiv1.name + '.' + views.ListIvornCitedCount.view_name)
            rv = self.c.get(url)
        assert rv.status_code == 200
        rd = json.loads(rv.data.decode())
        ivorn_citecounts = rd[ResultKeys.result]
        counts = list(zip(*ivorn_citecounts))[1]
        assert sum(counts) == n_internal_citations
        for ivorn, citecount in ivorn_citecounts:
            assert citecount == dbinf.cite_counts[ivorn]

    def test_xml_retrieval(self, simple_populated_db):
        url = url_for(apiv1.name + '.packet_xml')
        url += quote_plus(simple_populated_db.absent_ivorn)
        rv = self.c.get(url)
        assert rv.status_code == 422

        present_ivorn = simple_populated_db.inserted_ivorns[0]
        present_ivorn_xml_content = simple_populated_db.insert_packets_dumps[0]
        url = url_for(apiv1.name + '.packet_xml')
        url += quote_plus(present_ivorn)
        rv = self.c.get(url)
        assert rv.status_code == 200
        assert rv.mimetype == 'text/xml'
        assert rv.data.decode() == present_ivorn_xml_content.decode()

    def test_synopsis_view(self, simple_populated_db):
        # Null case, ivorn not in DB:
        ep_url = url_for(apiv1.name + '.packet_synopsis')
        url = ep_url + quote_plus(simple_populated_db.absent_ivorn)
        rv = self.c.get(url)
        assert rv.status_code == 422

        # Positive case, ivorn which has references:
        ivorn_w_refs = list(simple_populated_db.followup_packets)[0]
        url = ep_url + quote_plus(ivorn_w_refs)
        rv = self.c.get(url)
        assert rv.status_code == 200
        rd = json.loads(rv.data.decode())
        full = rd[ResultKeys.result]
        etree = simple_populated_db.packet_dict[ivorn_w_refs]
        assert len(full['refs']) == len(Cite.from_etree(etree))

        # Negative case, IVORN present but packet contains no references
        all_ivorns = set(simple_populated_db.packet_dict.keys())
        ivorns_wo_refs = list(
            all_ivorns - set(simple_populated_db.followup_packets))
        ivorn = ivorns_wo_refs[0]
        url = ep_url + quote_plus(ivorn)
        rv = self.c.get(url)
        assert rv.status_code == 200
        rd = json.loads(rv.data.decode())
        full = rd[ResultKeys.result]
        assert len(full['refs']) == 0

        # Find packet which cites a SWIFT GRB, check URLs looked up correctly:
        ref_string = 'BAT_GRB'
        url = url_for(apiv1.name + '.' + views.ListIvorn.view_name,
                      **{filters.RefContains.querystring_key: ref_string}
                      )
        rv = self.c.get(url)
        ref_lists = [Cite.from_etree(p)
                     for p in simple_populated_db.insert_packets
                     if Cite.from_etree(p)]
        matches = []
        for rl in ref_lists:
            for r in rl:
                if ref_string in r.ref_ivorn:
                    matches.append(r)
                    continue
        matched_via_restapi = json.loads(rv.data.decode())[ResultKeys.result]
        assert len(matched_via_restapi) == len(matches)
        url = ep_url + quote_plus(matched_via_restapi[0])
        rv = self.c.get(url)
        rd = json.loads(rv.data.decode())[ResultKeys.result]
        # When referencing a Swift alert, we should annotate for two urls,
        # GCN.gsfc.nasa.gov / www.swift.ac.uk
        assert len(rd['relevant_urls']) == 2


class TestSpatialFilters:
    @pytest.fixture(autouse=True)
    def assign_test_client_and_initdb(self, flask_test_client,
                                      fixture_db_session):
        self.c = flask_test_client  # Purely for brevity
        n_packets = 17
        packets = heartbeat_packets(n_packets=n_packets)
        for counter, pkt in enumerate(packets, start=1):
            packet_dec = 180.0 / n_packets * counter - 90
            coords = vp.Position2D(
                ra=15, dec=packet_dec, err=0.1,
                units=vp.definitions.units.degrees,
                system=vp.definitions.sky_coord_system.utc_icrs_geo)
            # print "Inserting coords", coords
            vp.add_where_when(
                pkt,
                coords=coords,
                obs_time=iso8601.parse_date(pkt.Who.Date.text),
                observatory_location=vp.definitions.observatory_location.geosurface
            )
        self.packets = packets
        self.ivorn_dec_map = {}
        for pkt in self.packets:
            posn = vp.get_event_position(pkt)
            self.ivorn_dec_map[pkt.attrib['ivorn']] = posn.dec
            fixture_db_session.add(Voevent.from_etree(pkt))

    def test_dec_gt(self):
        min_dec = -33.2
        url = url_for(apiv1.name + '.' + views.ListIvorn.view_name,
                      **{filters.DecGreaterThan.querystring_key: min_dec}
                      )
        with self.c as c:
            rv = self.c.get(url)
        rd = json.loads(rv.data.decode())[ResultKeys.result]
        matching_ivorns = [ivorn for ivorn in self.ivorn_dec_map
                           if self.ivorn_dec_map[ivorn] > min_dec]
        assert len(rd) == len(matching_ivorns)
        # print len(rd)

    def test_dec_lt(self):
        max_dec = -33.2
        url = url_for(apiv1.name + '.' + views.ListIvorn.view_name,
                      **{filters.DecLessThan.querystring_key: max_dec}
                      )
        with self.c as c:
            rv = self.c.get(url)
        rd = json.loads(rv.data.decode())[ResultKeys.result]
        matching_ivorns = [ivorn for ivorn in self.ivorn_dec_map
                           if self.ivorn_dec_map[ivorn] < max_dec]
        assert len(rd) == len(matching_ivorns)

    def test_dec_gt_and_lt(self):
        max_dec = 33.2
        min_dec = 10.2
        url = url_for(apiv1.name + '.' + views.ListIvorn.view_name,
                      **{filters.DecLessThan.querystring_key: max_dec,
                         filters.DecGreaterThan.querystring_key: min_dec,
                         }
                      )
        with self.c as c:
            rv = self.c.get(url)
        rd = json.loads(rv.data.decode())[ResultKeys.result]
        matching_ivorns = [ivorn for ivorn in self.ivorn_dec_map
                           if self.ivorn_dec_map[ivorn] < max_dec
                           and self.ivorn_dec_map[ivorn] > min_dec
                           ]
        assert len(rd) == len(matching_ivorns)
