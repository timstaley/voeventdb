import os
import fnmatch
import logging


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


