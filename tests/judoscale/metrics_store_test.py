import unittest
from unittest import TestCase
from judoscale.core.metrics_store import MetricsStore
import time


class TestMetricsStore(TestCase):
    def setUp(self):
        self.store = MetricsStore()

    def test_add_and_flush(self):
        self.store.add(11)
        self.store.add(22)

        assert self.store.flush() == [22, 11]
        assert self.store.flush() == []

    def test_max_flush_interval(self):
        self.store.max_flush_interval=0.0001
        self.store.add(11)
        time.sleep(0.01)

        # This add should be a no-op since it's been too long since the last flush
        self.store.add(22)

        assert self.store.flush() == [11]

        self.store.add(22)

        assert self.store.flush() == [22]


if __name__ == '__main__':
    unittest.main()
