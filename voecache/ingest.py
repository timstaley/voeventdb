import sys
import os
import fnmatch
import argparse
import logging
from lxml import etree

from voecache.models import  Voevent

logger = logging.getLogger(__name__)

def ingest_dir(topdir, session):
    logger.info("Scanning: " + topdir)
    xml_files = []
    for root, dirnames, filenames in os.walk(topdir):
        for filename in fnmatch.filter(filenames, '*.xml'):
            xml_files.append(os.path.join(root, filename))
    
    logger.info("Found: {} xml files".format(len(xml_files)))
    for idx, file_path in enumerate(xml_files):
        logger.debug("Ingesting {} of {}".format(idx, len(xml_files)))
        ingest_xml_file(file_path, session)


def ingest_xml_file(path, session):
    with open(path) as f:
        pkt_str = f.read()
    pkt_tree = etree.fromstring(pkt_str)
    ivorn = pkt_tree.attrib['ivorn']
    voevent_row = Voevent(ivorn=ivorn, packet=pkt_str)
    session.add(voevent_row)
