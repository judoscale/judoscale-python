import unittest
from datetime import datetime
from unittest import TestCase

from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import WebMetricsCollector
from judoscale.core.reporter import Reporter


class TestReporter(TestCase):
    def setUp(self):
        self.reporter = Reporter()

    def test_build_report(self):
        dt = datetime.fromisoformat("2012-12-12T12:12:00+00:00")
        metric = Metric(measurement="test", timestamp=dt.timestamp(), value=123)

        report = self.reporter._build_report([metric])

        assert list(report.keys()).sort() == ["config", "dyno", "pid", "metrics"].sort()
        assert len(report["metrics"]) == 1
        assert report["metrics"][0] == (1355314320, 123, "test", None)

    def test_add_collector(self):
        collector_instance = WebMetricsCollector()
        self.reporter.add_collector(collector_instance)
        assert self.reporter.collectors == [collector_instance]

    def test_find_collector(self):
        collector_instance = WebMetricsCollector()
        self.reporter.add_collector(collector_instance)
        assert self.reporter.find_collector(WebMetricsCollector) == collector_instance

    def test_cannot_find_collector(self):
        assert self.reporter.find_collector(WebMetricsCollector) is None

    def test_all_metrics_empty(self):
        assert self.reporter.all_metrics == []

    def test_all_metrics_not_empty(self):
        collector_instance_1 = WebMetricsCollector()
        collector_instance_2 = WebMetricsCollector()
        self.reporter.add_collector(collector_instance_1)
        self.reporter.add_collector(collector_instance_2)
        collector_instance_1.store.add(Metric(measurement="qt", timestamp=0, value=0))
        collector_instance_2.store.add(Metric(measurement="qt", timestamp=0, value=0))
        assert len(self.reporter.all_metrics) == 2


if __name__ == "__main__":
    unittest.main()
