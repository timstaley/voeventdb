from __future__ import absolute_import
from voeventdb.server.database.models import Voevent, Cite, Coord
from sqlalchemy import func, exists
from sqlalchemy.orm import aliased


def authored_month_counts_q(session):
    s = session
    # Careful with the datetime-truncation here - ensure we're working in UTC
    # before we bin by month!
    month_counts_qry = s.query(
        func.date_trunc('month',
                        func.timezone('UTC',Voevent.author_datetime)
                        ).distinct().label('month_id'),
        (func.count(Voevent.ivorn)).label('month_count'),
    ).select_from(Voevent).group_by('month_id')
    return month_counts_qry

def coord_cone_search_clause(ra, dec, radius):
    cone_search = func.q3c_radial_query(
                Coord.ra, Coord.dec,
                ra, dec, radius
            )
    return cone_search

def ivorn_cites_to_others_count_q(session):
    cites_to_others_count_qry = session.query(
        Voevent.ivorn.label('ivorn'),
        func.count(Cite.id).label('ref_count')
    ).outerjoin(Cite).group_by(Voevent.id)
    return cites_to_others_count_qry


def ivorn_cited_from_others_count_q(session):
    cite2 = aliased(Cite)
    cites_from_others_count_qry = session.query(
        Voevent.ivorn.label('ivorn'),
        func.count(cite2.id).label('citation_count')
    ).outerjoin(cite2, cite2.ref_ivorn == Voevent.ivorn).group_by(Voevent.id)
    return cites_from_others_count_qry


def _missing_cites_clause():
    voevent2 = aliased(Voevent)
    missing_cites_condition = ~exists().where(Cite.ref_ivorn == voevent2.ivorn)
    return missing_cites_condition


def missing_cites_q(session):
    return session.query(Cite.ref_ivorn). \
        filter(_missing_cites_clause())


def packet_with_missing_cites_q(session):
    return session.query(Voevent.ivorn). \
        filter(Voevent.cites.any(_missing_cites_clause()))


def role_counts_q(session):
    s = session
    role_counts_qry = s.query(
        Voevent.role.distinct().label('role_id'),
        (func.count(Voevent.ivorn)).label('role_count'),
    ).select_from(Voevent). \
        group_by(Voevent.role)
    return role_counts_qry


def stream_counts_q(session):
    s = session
    stream_counts_qry = s.query(
        Voevent.stream.distinct().label('stream_id'),
        (func.count(Voevent.ivorn)).label('stream_count'),
    ).select_from(Voevent). \
        group_by(Voevent.stream)
    return stream_counts_qry


def stream_counts_role_breakdown_q(session):
    s = session
    stream_counts_role_breakdown_qry = s.query(
        Voevent.stream.distinct().label('stream_id'),
        Voevent.role,
        (func.count(Voevent.ivorn)).label('stream_role_count'),
    ).select_from(Voevent). \
        group_by(Voevent.stream, Voevent.role)

    return stream_counts_role_breakdown_qry
