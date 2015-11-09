import tarfile
from cStringIO import StringIO
import voeventparse
import os

import logging
logger = logging.getLogger(__name__)

def bytestring_to_tar_tuple(filename, s):
    """
    Take a string + filename, return a (tarinfo, stringbuf) tuple for insertion.

    Args:
        s (string): Bytestring representation of the filedata.
        filename (string): Filepath relative to tarfile root.
    Returns:
        tuple: (tarfile.TarInfo,cstring.StringIO).
            This can be passed directly to TarFile.addfile().
    """
    info = tarfile.TarInfo(filename)
    info.size = len(s)
    return info, StringIO(s)


def filename_from_ivorn(ivorn):
    """
    Derive a sensible folder / filename path from ivorn.

    Args:
        ivorn (string): IVORN identifier including 'ivo://' prefix.
    Returns:
        string: relative path for xml output file.
    """
    return ivorn.split('//')[1].replace('#', '/') + '.xml'


def voevent_to_ivorn_xml_tuple(voevent):
    """
    Args:
        voevent (etree): Root of an lxml.etree loaded with voeventparse.
    """
    return (voevent.attrib['ivorn'], voeventparse.dumps(voevent))


def write_tarball(ivorn_xml_tuples, filepath):
    """
    Iterative over a series of ivorn / xml tuples and write to bz'd tarball.

    Args:
        ivorn_xml_tuples (iterable): [(ivorn,xml)]
            An iterable (e.g. list) of tuples containing two entries -
            an ivorn string and an xml bytestring.
        filepath (string): Path to the new tarball to create. Typically of form
            '/path/to/foo.tar.bz2'
    Returns
        packet_count (int): Number of packets written to tarball
    """
    out = tarfile.open(filepath, mode='w:bz2')
    logger.info("Writing packets to tarball at " + filepath)
    packet_count = 0
    try:
        for (ivorn, xml) in ivorn_xml_tuples:
            out.addfile(*bytestring_to_tar_tuple(
                filename_from_ivorn(ivorn),
                xml
            ))
            packet_count+=1
    finally:
        out.close()
    return packet_count

def tarfile_xml_generator(fname):
    """
    Generator for iterating through xml files in a tarball.

    Returns strings.

    Example usage::

        xmlgen = tarfile_xml_generator(fname)
        xml0 = next(xmlgen)

        for pkt in xmlgen:
            foo(pkt)

    """
    tf = tarfile.open(fname, mode='r')
    try:
        tarinf = tf.next()
        while tarinf is not None:
            if tarinf.isfile() and tarinf.name[-4:] == '.xml':
                fbuf = tf.extractfile(tarinf)
                tarinf.xml = fbuf.read()
                yield tarinf
            tarinf = tf.next()
            # Kludge around tarfile memory leak, cf
            # http://blogs.it.ox.ac.uk/inapickle/2011/06/20/high-memory-usage-when-using-pythons-tarfile-module/
            tf.members = []
    finally:
        tf.close()
