from __future__ import absolute_import
import tempfile
import os
import voeventcache.tests.fixtures.fake as fake
import pytest
import voeventcache.utils.filestore as filestore


@pytest.yield_fixture
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
    print "Wrote ",len(voevents), "to", fname


