import voeventparse
from voeventcache.tests.resources.datapaths import swift_bat_grb_pos_v2_filepath
with open(swift_bat_grb_pos_v2_filepath) as f:
    swift_bat_grb_pos_v2_etree = voeventparse.load(f)