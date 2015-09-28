from __future__ import absolute_import

import voeventparse as vp
from voeventcache.database.models import Voevent
from sqlalchemy import func

import logging

logger = logging.getLogger(__name__)


def ivorn_present(session, ivorn):
    """
    Predicate, returns whether the IVORN is in the database.
    """
    return bool(
        session.query(Voevent.id).filter(Voevent.ivorn == ivorn).count())


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


def stream_counts(session):
    s = session
    stream_counts_qry = s.query(
            Voevent.stream.distinct().label('streamid'),
            (func.count(Voevent.ivorn)).label('streamcount'),
        ).select_from(Voevent).\
        group_by(Voevent.stream).\
        order_by('streamcount')
    return stream_counts_qry


def stream_counts_role_breakdown(session):
    s = session
    stream_counts_role_breakdown_qry = s.query(
            Voevent.stream.distinct().label('streamid'),
            Voevent.role,
            (func.count(Voevent.ivorn)).label('streamcount'),
        ).select_from(Voevent).\
            group_by(Voevent.stream, Voevent.role).\
        order_by(Voevent.stream, Voevent.role)
    return stream_counts_role_breakdown_qry

