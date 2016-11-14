import os
from voeventdb.server.tests.resources import __path__ as data_dir

data_dir = data_dir[0]
swift_bat_grb_pos_v2_filepath = os.path.join(
    data_dir,
    'SWIFT_bat_position_v2.0_example.xml')

swift_bat_grb_655721_filepath = os.path.join(data_dir,
                                             'BAT_GRB_Pos_655721-214.xml')
swift_xrt_grb_655721_filepath = os.path.join(data_dir, 'XRT_Pos_655721-326.xml')

konus_lc_filepath = os.path.join(data_dir,
                                 'Konus_Lightcurve_2015-07-10T00:28:01.68.xml')

gaia_16bsf_filepath = os.path.join(data_dir, 'Gaia16bsf.xml')

assasn_non_ascii_packet_filepath = os.path.join(
    data_dir,
    'ASASSN#2016-09-25.47_2016fvf_PTSS-16nqb_PS16ejf.xml')
