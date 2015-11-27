from __future__ import absolute_import
import voeventparse as vp
from voeventdb.server.utils.filestore import tarfile_xml_generator
from voeventdb.server.database.models import Voevent
from voeventdb.server.database.convenience import ivorn_present
import sys

import logging

logger = logging.getLogger(__name__)


def load_from_tarfile(session, tarfile_path, check_for_duplicates,
                      pkts_per_commit=1000):
    """
    Iterate through xml files in a tarball and attempt to load into database.

    .. warning::
        Very slow with duplicate checking enabled.

    Returns:
        tuple: (n_parsed, n_loaded) - Total number of packets parsed from
            tarbar, and number successfully loaded.

    """
    tf_stream = tarfile_xml_generator(tarfile_path)
    logger.info("Loading: " + tarfile_path)
    n_parsed = 0
    n_loaded = 0
    for tarinf in tf_stream:
        try:
            v = vp.loads(tarinf.xml, check_version=False)
            if v.attrib['version'] != '2.0':
                logger.debug(
                    'Packet: {} is not VO-schema version 2.0.'.format(
                        tarinf.name))
            n_parsed += 1
        except:
            logger.exception('Error loading file {}, skipping'.format(
                tarinf.name))
            continue
        try:
            new_row = Voevent.from_etree(v)
            if check_for_duplicates:
                if ivorn_present(session, new_row.ivorn):
                    logger.debug(
                        "Ignoring duplicate ivorn: {} in file {}".format(
                            new_row.ivorn, tarinf.name))
                    continue
            session.add(new_row)
            n_loaded += 1
        except:
            logger.exception(
                'Error converting file {} to database row, skipping'.
                    format(tarinf.name))
            continue

        if n_loaded % pkts_per_commit == 0:
            session.commit()
    session.commit()
    logger.info("Successfully parsed {} packets, of which loaded {}.".format(n_parsed, n_loaded))
    return n_parsed, n_loaded
