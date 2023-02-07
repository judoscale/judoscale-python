import unittest
from datetime import datetime
from unittest import TestCase

from judoscale.core.config import config
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import WebMetricsCollector
from judoscale.core.reporter import Reporter


class TestReporter(TestCase):
    def setUp(self):
        self.reporter = Reporter()
        # Simulate web dyno
        config.dyno, config.dyno_name, config.dyno_num = "web.1", "web", 1

    def test_build_report(self):
        dt = datetime.fromisoformat("2012-12-12T12:12:00+00:00")
        metric = Metric(measurement="test", timestamp=dt.timestamp(), value=123)

        report = self.reporter._build_report([metric])

        assert list(report.keys()).sort() == ["config", "dyno", "pid", "metrics"].sort()
        assert len(report["metrics"]) == 1
        assert report["metrics"][0] == (1355314320, 123, "test", None)

    def test_add_collector(self):
        collector_instance = WebMetricsCollector(config)
        self.reporter.add_collector(collector_instance)
        assert self.reporter.collectors == [collector_instance]

    def test_all_metrics_empty(self):
        assert self.reporter.all_metrics == []

    def test_all_metrics_not_empty(self):
        collector_instance_1 = WebMetricsCollector(config)
        collector_instance_2 = WebMetricsCollector(config)
        self.reporter.add_collector(collector_instance_1)
        self.reporter.add_collector(collector_instance_2)
        collector_instance_1.add(Metric(measurement="qt", timestamp=0, value=0))
        collector_instance_2.add(Metric(measurement="qt", timestamp=0, value=0))
        assert len(self.reporter.all_metrics) == 2


if __name__ == "__main__":
    unittest.main()
