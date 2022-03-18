from judoscale.core.metrics_store import MetricsStore

class TestMetricsStore:
    def test_add_and_flush(self):
        store = MetricsStore()
        store.add(11)
        store.add(22)

        assert store.flush() == [22, 11]
        assert store.flush() == []
