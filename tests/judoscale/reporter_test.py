import unittest
from unittest import TestCase

from src.judoscale.core.reporter import Reporter
from src.judoscale.core.metric import Metric
from datetime import datetime


class TestReporter(TestCase):
    def setUp(self):
        self.reporter = Reporter()

    def test_build_report(self):
        dt = datetime.fromisoformat("2012-12-12T12:12:00+00:00")
        metric = Metric(measurement="test", datetime=dt, value=123.456789)

        report = self.reporter._build_report([metric])

        assert list(report.keys()).sort() == [
            "config", "dyno", "pid", "metrics"
        ].sort()
        assert len(report["metrics"]) == 1
        assert report["metrics"][0] == [1355314320, 123.46, "test", None]


if __name__ == '__main__':
    unittest.main()
