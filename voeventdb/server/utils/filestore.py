import tarfile
from io import BytesIO
import voeventparse
import os

import logging

logger = logging.getLogger(__name__)


def bytestring_to_tar_tuple(filename, bytes):
    """
    Take a string + filename, return a (tarinfo, stringbuf) tuple for insertion.

    Args:
        bytes (bstring): Bytestring representation of the filedata.
        filename (string): Filepath relative to tarfile root.
    Returns:
        tuple: (tarfile.TarInfo,io.BytesIO).
            This can be passed directly to TarFile.addfile().
    """
    info = tarfile.TarInfo(filename)
    info.size = len(bytes)
    return info, BytesIO(bytes)


def filename_from_ivorn(ivorn):
    """
    Derive a sensible folder / filename path from ivorn.

    Args:
        ivorn (string): IVORN identifier including 'ivo://' prefix.
    Returns:
        string: relative path for xml output file.
    """
    return ivorn.split('//')[1].replace('#', '/') + '.xml'


def voevent_etree_to_ivorn_xml_tuple(voevent):
    """
    Args:
        voevent (etree): Root of an lxml.etree loaded with voeventparse.
    """
    return (voevent.attrib['ivorn'], voeventparse.dumps(voevent))


def voevent_dbrow_to_ivorn_xml_tuple(voevent):
    """
    Args:
        voevent (:class:`voeventdb.server.database.models.Voevent`): Voevent
            model / data-tuple as retrieved from the database
    """
    # This is a horrible kludge, we should know whether the datatype is
    # a bytestring or unicode string by design. (In practice, the uncertainty
    # is only encountered during unit-tests, all real-world usage deals with
    # the unicode case. But that means the tests didn't catch bugs!)
    # It will do as a temporary fix, to allow data-dumps from the live
    # database.
    # Will soon port to Python3 with Postgres BYTEA storage and get things properly
    # configured.
    xml = voevent.xml
    if isinstance(xml, unicode):
        return (voevent.ivorn, voevent.xml.encode('utf-8'))
    return (voevent.ivorn, voevent.xml)


def write_tarball(voevents, filepath):
    """
    Iterate over voevent models / dbrows and write to bz'd tarball.

    Args:
        voevents (iterable): An iterable (e.g. list) of e.g. Voevent db-rows,
            with access to the 'ivorn' and 'xml' attributes.
        filepath (string): Path to the new tarball to create. Typically of form
            '/path/to/foo.tar.bz2'
    Returns
        packet_count (int): Number of packets written to tarball
    """
    tuple_gen = (voevent_dbrow_to_ivorn_xml_tuple(v) for v in voevents)
    return write_tarball_from_ivorn_xml_tuples(tuple_gen,
                                               filepath)


def write_tarball_from_ivorn_xml_tuples(ivorn_xml_tuples, filepath):
    """
    Iterate over a series of ivorn / xml bstring tuples and write to bz'd tarball.

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
            packet_count += 1
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
