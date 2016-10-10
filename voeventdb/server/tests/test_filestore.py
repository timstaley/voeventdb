from __future__ import absolute_import
import tempfile
import os
import voeventdb.server.tests.fixtures.fake as fake
import pytest
import tarfile
import voeventdb.server.utils.filestore as filestore
import voeventparse as vp


@pytest.fixture
def named_temporary_file():
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.close()
    yield temp_file
    os.unlink(temp_file.name)


def test_tarball_dump(named_temporary_file):
    voevents = fake.heartbeat_packets()
    voevent_gen = (v for v in voevents)
    fname = named_temporary_file.name
    filestore.write_tarball(
        (filestore.voevent_to_ivorn_xml_tuple(v) for v in voevent_gen),
        fname
    )
    tarball = tarfile.open(fname)
    assert len(tarball.getmembers()) == len (voevents)


def test_tarball_round_trip(named_temporary_file):
    voevents = fake.heartbeat_packets()
    fname = named_temporary_file.name
    filestore.write_tarball(
        (filestore.voevent_to_ivorn_xml_tuple(v) for v in voevents),
        fname
    )

    loaded_voevents = [ vp.loads(s.xml) for s in filestore.tarfile_xml_generator(fname)]
    def to_strings(voeventlist):
        return [vp.dumps(v) for v in voeventlist]
    def to_ivorn(voeventlist):
        return [v.attrib['ivorn'] for v in voeventlist]

    assert (to_ivorn(voevents) == to_ivorn(loaded_voevents))
    assert (to_strings(voevents) == to_strings(loaded_voevents))