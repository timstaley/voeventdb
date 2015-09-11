from voeventcache.tests.fixtures import packetgen
from voeventcache.tests.fixtures.testpacket_id import testpacket_identity
from datetime import datetime, timedelta


def heartbeat_packets(start=datetime(2015, 1, 1),
                      interval=timedelta(minutes=15),
                      n_packets=24):
    """

    Args:
        start(datetime.datetime): Start time.
        end(datetime.datetime): End time (non-inclusive).
        interval(datetime.timedelta): Heartbeat interval.
    Returns:
        packets: A list of VOEvent packets.
    """
    packets = []
    for ts in packetgen.timerange(start,start+n_packets*interval,interval):
        packets.append(packetgen.create_test_packet(testpacket_identity,
                                                    author_date=ts))
    return packets