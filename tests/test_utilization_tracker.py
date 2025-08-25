import logging
from datetime import datetime

from pytest import fixture

from judoscale.core.metric import Metric
from judoscale.core.metrics_store import MetricsStore
from judoscale.core.utilization_tracker import UtilizationTracker


@fixture
def utilization_tracker():
    tracker = UtilizationTracker(store=MetricsStore())
    yield tracker
    tracker.stop()


class TestUtilizationTracker:
    def test_tracks_utilization_metrics_for_active_requests(self, utilization_tracker):
        def metrics_measurements(metrics):
            return list(map(lambda m: [m.measurement, m.value], metrics))

        utilization_tracker._track_current_state()

        metrics = utilization_tracker.store.flush()
        assert metrics_measurements(metrics) == [["ru", 0], ["pu", 0]]

        utilization_tracker.incr()
        utilization_tracker.incr()
        utilization_tracker._track_current_state()

        metrics = utilization_tracker.store.flush()
        assert metrics_measurements(metrics) == [["ru", 2], ["pu", 1]]

        utilization_tracker.decr()
        utilization_tracker._track_current_state()

        metrics = utilization_tracker.store.flush()
        assert metrics_measurements(metrics) == [["ru", 1], ["pu", 1]]

        utilization_tracker.decr()
        utilization_tracker._track_current_state()

        metrics = utilization_tracker.store.flush()
        assert metrics_measurements(metrics) == [["ru", 0], ["pu", 0]]
