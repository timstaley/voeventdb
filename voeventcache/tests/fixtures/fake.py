from voeventcache.tests.fixtures import packetgen
from voeventcache.tests.fixtures.testpacket_id import testpacket_identity
from datetime import datetime, timedelta
import voeventparse as vp

def heartbeat_packets(start=datetime(2015, 1, 1),
                      interval=timedelta(minutes=15),
                      n_packets=24):
    """
    Create Voevents with varying ivorns and values of ``Who.Date``.

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


    # NB Whitespacing of loaded (parsed) vs custom-built VOEvents is different:
    # http://lxml.de/FAQ.html#why-doesn-t-the-pretty-print-option-reformat-my-xml-output
    # So, to enable exact ``dumps`` matching (for equality testing)
    # we take the fake voevents on a save/load round-trip before we return
    packets = [ vp.loads(vp.dumps(v)) for v in packets]

    return packets