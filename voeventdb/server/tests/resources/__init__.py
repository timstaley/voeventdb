from __future__ import absolute_import, unicode_literals
import voeventparse
from voeventdb.server.tests.resources.datapaths import (
    assasn_non_ascii_packet_filepath,
    gaia_16bsf_filepath,
    konus_lc_filepath,
    swift_bat_grb_pos_v2_filepath,
    swift_bat_grb_655721_filepath,
    swift_xrt_grb_655721_filepath
)
with open(swift_bat_grb_pos_v2_filepath, 'rb') as f:
    swift_bat_grb_pos_v2_etree = voeventparse.load(f)

#NB xrt_grb_655721 cites -> bat_grb_655721
with open(swift_bat_grb_655721_filepath, 'rb') as f:
    swift_bat_grb_655721 = voeventparse.load(f)
with open(swift_xrt_grb_655721_filepath, 'rb') as f:
    swift_xrt_grb_655721 = voeventparse.load(f)

with open(konus_lc_filepath, 'rb') as f:
    konus_lc = voeventparse.load(f)

with open(gaia_16bsf_filepath, 'rb') as f:
    gaia_16bsg = voeventparse.load(f)
