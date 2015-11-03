import voeventparse
from voeventdb.tests.resources.datapaths import (
    konus_lc_filepath,
    swift_bat_grb_pos_v2_filepath,
    swift_bat_grb_655721_filepath,
    swift_xrt_grb_655721_filepath
)
with open(swift_bat_grb_pos_v2_filepath) as f:
    swift_bat_grb_pos_v2_etree = voeventparse.load(f)

#NB xrt_grb_655721 cites -> bat_grb_655721
with open(swift_bat_grb_655721_filepath) as f:
    swift_bat_grb_655721 = voeventparse.load(f)
with open(swift_xrt_grb_655721_filepath) as f:
    swift_xrt_grb_655721 = voeventparse.load(f)

with open(konus_lc_filepath) as f:
    konus_lc = voeventparse.load(f)

