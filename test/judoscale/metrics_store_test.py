from judoscale.core.metrics_store import MetricsStore

class TestMetricsStore:
    def test_add_and_flush(self):
        store = MetricsStore()
        store.add(11)
        store.add(22)
        metrics = store.flush()

        assert metrics == [22, 11]
