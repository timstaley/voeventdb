from __future__ import absolute_import
from voeventdb.server.database.models import Voevent
from sqlalchemy import func
import voeventdb.server.database.query as query

import logging

logger = logging.getLogger(__name__)


def ivorn_present(session, ivorn):
    """
    Predicate, returns whether the IVORN is in the database.
    """
    return bool(
        session.query(Voevent.id).filter(Voevent.ivorn == ivorn).count())

def ivorn_prefix_present(session, ivorn_prefix):
    """
    Predicate, returns whether there is an entry in the database with matching
    IVORN prefix.
    """
    n_matches = session.query(Voevent.ivorn).filter(
            Voevent.ivorn.like('{}%'.format(ivorn_prefix))).count()
    return bool(n_matches)


def safe_insert_voevent(session, etree):
    """
    Insert a VOEvent, or skip with a warning if it's a duplicate.

    NB XML contents are checked to confirm duplication - if there's a mismatch,
    we raise a ValueError.
    """
    new_row = Voevent.from_etree(etree)
    if not ivorn_present(session, new_row.ivorn):
        session.add(new_row)
    else:
        old_xml = session.query(Voevent.xml).filter(
            Voevent.ivorn == new_row.ivorn).scalar()
        if old_xml != new_row.xml:
            raise ValueError('Tried to load a VOEvent with duplicate IVORN,'
                             'but XML contents differ - not clear what to do.')
        else:
            logger.warn('Skipping insert for packet with duplicate IVORN, '
                        'XML matches OK.')



def to_nested_dict(bi_grouped_rowset):
    nested = {}
    for r in bi_grouped_rowset:
        if r[0] not in nested:
            nested[r[0]]={}
        nested[r[0]][r[1]] = r[2]
    return nested
