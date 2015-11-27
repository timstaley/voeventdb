"""
Routines for determining relevant information implied by, but not contained in,
VOEvent packets.
"""
from voeventdb.server.database.models import Voevent, Cite

_swift_stream = "nasa.gsfc.gcn/SWIFT"
_swift_grb_pos_prefix = 'ivo://nasa.gsfc.gcn/SWIFT#BAT_GRB_Pos_'


def lookup_relevant_urls(voevent_row, cite_rows):
    assert isinstance(voevent_row, Voevent)
    urls = []
    urls.extend(lookup_swift_urls(voevent_row,cite_rows))
    return urls


def _pull_swift_trig_id_from_ivorn(ivorn):
    swift_id = ivorn[len(_swift_grb_pos_prefix):]
    swift_id = swift_id.split('-')[0]
    return swift_id


def lookup_swift_urls(voevent_row, cite_rows):
    swift_id = None
    if voevent_row.ivorn.startswith(_swift_grb_pos_prefix):
        swift_id = _pull_swift_trig_id_from_ivorn(voevent_row.ivorn)
    else:
        for row in cite_rows:
            if row.ref_ivorn.startswith(_swift_grb_pos_prefix):
                swift_id = _pull_swift_trig_id_from_ivorn(row.ref_ivorn)

    urls = []
    if swift_id:
        urls.append(
            "http://www.swift.ac.uk/search/summary.php?obsid={}".format(
                swift_id)
        )
        urls.append(
            "http://gcn.gsfc.nasa.gov/other/{}.swift".format(swift_id)
        )
    return urls
