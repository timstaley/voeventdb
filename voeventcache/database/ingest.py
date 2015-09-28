from __future__ import absolute_import
import voeventparse as vp
from voeventcache.utils.filestore import tarfile_xml_generator
from voeventcache.database.models import Voevent
import sys

import logging
logger = logging.getLogger(__name__)


def load_from_tarfile(session, tarfile_path, pkts_per_commit=10000):
    tf_stream = tarfile_xml_generator(tarfile_path)
    logger.info("Loading: " + tarfile_path)
    count = 0
    for tarinf in tf_stream:

        try:
            v = vp.loads(tarinf.xml,check_version=False)
            if v.attrib['version'] !='2.0':
                logger.debug(
                    'Packet: {} is not VO-schema version 2.0.'.format(
                        tarinf.name))
        except:
            logger.exception('Error loading file {}, skipping'.format(
                                                            tarinf.name))
            continue
        try:
            new_row = Voevent.from_etree(v)
            session.add(new_row)
        except:
            logger.exception(
                'Error converting file {} to database row, skipping'.
                    format(tarinf.name))
            continue

        count += 1
        if count % pkts_per_commit == 0:
            session.commit()
    session.commit()
    logger.info("Loaded {} voevent packets.".format(count))
    return count

