from __future__ import absolute_import
from voeventdb.server.database.models import Voevent
from voeventdb.server.tests.fixtures import fake
from voeventdb.server.database.config import testdb_corpus_url
import voeventdb.server.database.db_utils as db_utils
import voeventparse
import pytest
import os
import sys
import subprocess
import sqlalchemy
import sqlalchemy.orm


def test_ingest_packet():
    #Must create corpusdb first:
    assert db_utils.check_database_exists(testdb_corpus_url)
    engine = sqlalchemy.create_engine(testdb_corpus_url)
    s = sqlalchemy.orm.Session(bind=engine)
    from voeventdb.server import __path__ as root_path
    root_path = root_path[0]
    script_path = os.path.join(root_path, 'bin', 'voeventdb_ingest_packet.py')

    print("Testing script at ", script_path)
    print("Using executable:", sys.executable)

        # Do stuff
    n_before = s.query(Voevent).count()
    proc = subprocess.Popen(
        [script_path,
         '-d={}'.format(testdb_corpus_url.database),
         '-l={}'.format('/tmp/vdbingest-test.log'),
         ],
        stdin=subprocess.PIPE,
    )
    proc.communicate(voeventparse.dumps(fake.heartbeat_packets(n_packets=1)[0]))
    proc.wait()

    assert proc.returncode == 0
    assert s.query(Voevent).count() == n_before + 1
