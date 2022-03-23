from judoscale.core.metrics_store import MetricsStore
import time

class TestMetricsStore:
    def test_add_and_flush(self):
        store = MetricsStore()
        store.add(11)
        store.add(22)

        assert store.flush() == [22, 11]
        assert store.flush() == []

    def test_max_flush_interval(self):
        store = MetricsStore(max_flush_interval=0.0001)
        store.add(11)
        time.sleep(0.01)

        # This add should be a no-op since it's been too long since the last flush
        store.add(22)

        assert store.flush() == [11]

        store.add(22)

        assert store.flush() == [22]
