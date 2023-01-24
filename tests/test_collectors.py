import json
import time
import unittest
from unittest import TestCase
from unittest.mock import Mock

import redis.exceptions

from judoscale.celery.collector import CeleryMetricsCollector
from judoscale.core.config import config
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import JobMetricsCollector, WebMetricsCollector


class TestWebMetricsCollector(TestCase):
    def test_should_collect(self):
        config.dyno, config.dyno_name, config.dyno_num = "web.1", "web", 1
        assert WebMetricsCollector(config).should_collect is True

    def test_should_not_collect(self):
        config.dyno, config.dyno_name, config.dyno_num = "worker.1", "worker", 1
        assert WebMetricsCollector(config).should_collect is False

    def test_add(self):
        config.dyno, config.dyno_name, config.dyno_num = "web.1", "web", 1
        collector = WebMetricsCollector(config)
        metric = Metric.for_web(f"t={time.time():.3f}")
        collector.add(metric)
        assert collector.store.store == [metric]

    def test_collect(self):
        config.dyno, config.dyno_name, config.dyno_num = "web.1", "web", 1
        collector = WebMetricsCollector(config)
        metric = Metric.for_web(f"t={time.time():.3f}")
        collector.add(metric)
        assert collector.collect() == [metric]
        assert collector.store.store == []


class TestJobMetricsCollector(TestCase):
    def test_should_collect_web_1(self):
        config.dyno, config.dyno_name, config.dyno_num = "web.1", "web", 1
        assert JobMetricsCollector(config).should_collect is True

    def test_should_not_collect_web_2(self):
        config.dyno, config.dyno_name, config.dyno_num = "web.2", "web", 2
        assert JobMetricsCollector(config).should_collect is False

    def test_should_collect_worker_1(self):
        config.dyno, config.dyno_name, config.dyno_num = "worker.1", "worker", 1
        assert JobMetricsCollector(config).should_collect is True

    def test_should_not_collect_worker_2(self):
        config.dyno, config.dyno_name, config.dyno_num = "worker.2", "worker", 2
        assert JobMetricsCollector(config).should_collect is False


if __name__ == "__main__":
    unittest.main()
