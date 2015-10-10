from __future__ import absolute_import
from voeventcache.database.models import Voevent
from sqlalchemy import func

def authored_month_counts_q(session):
    s = session
    month_counts_qry = s.query(
        func.date_trunc('month', Voevent.author_datetime).distinct().label(
            'month_id'),
        (func.count(Voevent.ivorn)).label('month_count'),
    ).select_from(Voevent).group_by('month_id')
    return month_counts_qry


def stream_counts_q(session):
    s = session
    stream_counts_qry = s.query(
        Voevent.stream.distinct().label('stream_id'),
        (func.count(Voevent.ivorn)).label('stream_count'),
    ).select_from(Voevent). \
        group_by(Voevent.stream)
    return stream_counts_qry


def role_counts_q(session):
    s = session
    role_counts_qry = s.query(
        Voevent.role.distinct().label('role_id'),
        (func.count(Voevent.ivorn)).label('role_count'),
    ).select_from(Voevent). \
        group_by(Voevent.role)
    return role_counts_qry


def stream_counts_role_breakdown_q(session):
    s = session
    stream_counts_role_breakdown_qry = s.query(
        Voevent.stream.distinct().label('stream_id'),
        Voevent.role,
        (func.count(Voevent.ivorn)).label('stream_role_count'),
    ).select_from(Voevent). \
        group_by(Voevent.stream, Voevent.role)

    return stream_counts_role_breakdown_qry



