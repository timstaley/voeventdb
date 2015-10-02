from __future__ import absolute_import
from voeventcache.database.models import Voevent
from sqlalchemy import func

def stream_counts_q(session):
    s = session
    stream_counts_qry = s.query(
        Voevent.stream.distinct().label('streamid'),
        (func.count(Voevent.ivorn)).label('streamcount'),
    ).select_from(Voevent). \
        group_by(Voevent.stream)
    return stream_counts_qry

def role_counts_q(session):
    s = session
    role_counts_qry = s.query(
        Voevent.role.distinct().label('roleid'),
        (func.count(Voevent.ivorn)).label('rolecount'),
    ).select_from(Voevent). \
        group_by(Voevent.role)
    return role_counts_qry

def stream_counts_role_breakdown_q(session):
    s = session
    stream_counts_role_breakdown_qry = s.query(
        Voevent.stream.distinct().label('streamid'),
        Voevent.role,
        (func.count(Voevent.ivorn)).label('stream_role_count'),
    ).select_from(Voevent). \
        group_by(Voevent.stream, Voevent.role)

    return stream_counts_role_breakdown_qry



