import tarfile
from cStringIO import StringIO
import voeventparse


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
    """
    out = tarfile.open(filepath, mode='w:bz2')
    try:
        for (ivorn, xml) in ivorn_xml_tuples:
            out.addfile(*bytestring_to_tar_tuple(
                filename_from_ivorn(ivorn),
                xml
            ))
    finally:
        out.close()
