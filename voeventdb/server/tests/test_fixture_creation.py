from __future__ import absolute_import
from unittest import TestCase
from datetime import datetime, timedelta
from voeventdb.server.tests.fixtures import fake, packetgen

class TestBasicRoutines(TestCase):
    def setUp(self):
        self.start = datetime(2015, 1, 1)
        self.interval = timedelta(minutes=15)

    def test_timerange(self):
        n_interval_added = 5
        times = [t for t in
                 packetgen.timerange(self.start,
                                     self.start+self.interval*n_interval_added,
                                     self.interval)]
        self.assertEqual(n_interval_added, len(times))
        self.assertEqual(self.start, times[0])


    def test_heartbeat(self):
        n_interval = 4*6
        packets = fake.heartbeat_packets(self.start, self.interval,
                                         n_interval)
        self.assertEqual(n_interval, len(packets))
