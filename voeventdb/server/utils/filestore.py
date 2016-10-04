import logging
import tarfile
import voeventparse
from collections import namedtuple
from io import BytesIO
import six
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
    tuple_gen = ( (v.ivorn, v.xml) for v in voevents)
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


class TarXML(namedtuple('TarXML', 'name xml')):
    """
    A namedtuple for pairing a filename and XML bytestring

    Attributes:
        name (str): Filename from the tarball
        xml (builtins.bytes): Bytestring containing the raw XML data.
    """
    pass  # Just wrapping a namedtuple so we can assign a docstring.




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
                yield TarXML(name=tarinf.name, xml=fbuf.read())
            tarinf = tf.next()
            # Kludge around tarfile memory leak, cf
            # http://blogs.it.ox.ac.uk/inapickle/2011/06/20/high-memory-usage-when-using-pythons-tarfile-module/
            tf.members = []
    finally:
        tf.close()
