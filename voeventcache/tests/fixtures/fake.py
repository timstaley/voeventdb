from voeventcache.tests.fixtures import packetgen
from voeventcache.tests.fixtures.testpacket_id import testpacket_identity



def heartbeat_packets(start, end, interval):
    """

    Args:
        start(datetime.datetime): Start time.
        end(datetime.datetime): End time (non-inclusive).
        interval(datetime.timedelta): Heartbeat interval.
    Returns:
        packets: A list of VOEvent packets.
    """
    packets = []
    for ts in packetgen.timerange(start,end,interval):
        packets.append(packetgen.create_test_packet(testpacket_identity,
                                                    author_date=ts))
    return packets