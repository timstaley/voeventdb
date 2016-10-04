#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import
import tempfile
import os
import voeventdb.server.tests.fixtures.fake as fake
import pytest
import tarfile
import voeventdb.server.utils.filestore as filestore
import voeventdb.server.database.models as models
import voeventparse as vp
import six
from voeventdb.server.tests.resources.datapaths import (
    assasn_non_ascii_packet_filepath,
)

@pytest.fixture
def named_temporary_file():
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    yield temp_file
    os.unlink(temp_file.name)


def test_simple_tarball_dump(named_temporary_file):
    voevent_etrees = fake.heartbeat_packets()
    voevent_rowgen = (models.Voevent.from_etree(v) for v in voevent_etrees)
    fname = named_temporary_file.name
    filestore.write_tarball(voevent_rowgen, fname)
    tarball = tarfile.open(fname)
    assert len(tarball.getmembers()) == len(voevent_etrees)


def test_bytestring_to_tar_tuple():
    path = '/foo/bar/baz'
    bytestring = b'foobar'
    filestore.bytestring_to_tar_tuple(path, bytestring)

    bytestring = u'foobar€€€'.encode('UTF-8')
    filestore.bytestring_to_tar_tuple(path, bytestring)


def test_unicode_to_tar_tuple():
    path = '/foo/bar/baz'
    string_containing_unicode = u'foobar€€€'
    filestore.bytestring_to_tar_tuple(path, string_containing_unicode.encode('utf-8'))


def test_unicode_voevent_tarball_dump(named_temporary_file):
    ## Now try some unicode characters
    voevent_etrees = fake.heartbeat_packets()
    vp.set_author(voevent_etrees[0], contactName=u"€€€€")
    voevent_rowgen = (models.Voevent.from_etree(v) for v in voevent_etrees)
    fname = named_temporary_file.name
    filestore.write_tarball(voevent_rowgen, fname)
    tarball = tarfile.open(fname)
    assert len(tarball.getmembers()) == len(voevent_etrees)


def test_tarball_round_trip(named_temporary_file, fixture_db_session):
    voevent_etrees = fake.heartbeat_packets()
    # with open(assasn_non_ascii_packet_filepath, 'rb') as f:
    #     voevent_etrees.append(vp.load(f))
    s = fixture_db_session
    for etree in voevent_etrees:
        s.add(models.Voevent.from_etree(etree))
    s.flush()
    voevent_dbrows = s.query(models.Voevent.ivorn, models.Voevent.xml).all()
    assert len(voevent_dbrows) == len(voevent_etrees)
    voevent_rowgen = list(models.Voevent.from_etree(v) for v in voevent_etrees)
    assert voevent_dbrows[0].ivorn == voevent_rowgen[0].ivorn
    assert voevent_dbrows[0].xml == voevent_rowgen[0].xml

    assert type(voevent_dbrows[0].xml) == type(voevent_rowgen[0].xml)
    assert type(voevent_rowgen[0].xml) == six.binary_type

    # Therefore it's crucial to test with an actual round-tripped dataset,
    # the 'voevent_dbrows' from above:
    fname = named_temporary_file.name
    filestore.write_tarball(voevent_dbrows, fname)

    loaded_voevents = [vp.loads(s.xml) for s in
                       filestore.tarfile_xml_generator(fname)]

    def to_strings(voeventlist):
        return [vp.dumps(v) for v in voeventlist]

    def to_ivorn(voeventlist):
        return [v.attrib['ivorn'] for v in voeventlist]

    assert (to_ivorn(voevent_etrees) == to_ivorn(loaded_voevents))
    assert (to_strings(voevent_etrees) == to_strings(loaded_voevents))
