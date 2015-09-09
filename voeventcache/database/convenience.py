from __future__ import absolute_import

from voeventcache.database.models import Voevent

def ivorn_present(session, ivorn):
    """
    Predicate, returns whether the IVORN is in the database.
    """
    return bool(session.query(Voevent.id).filter(Voevent.ivorn==ivorn).count())