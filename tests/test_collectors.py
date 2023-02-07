import json
import time
import unittest
from typing import List
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


class TestCeleryMetricsCollector(TestCase):
    def setUp(self):
        self.redis = Mock()
        self.connection = Mock(transport=Mock(driver_name="redis"))
        self.connection.configure_mock(
            **{"channel.return_value": Mock(client=self.redis)}
        )

        self.celery = Mock()
        self.celery.configure_mock(
            **{"connection_for_read.return_value": self.connection}
        )

    def test_incorrect_driver(self):
        self.connection.transport.driver_name = "not_redis"
        with self.assertRaises(NotImplementedError):
            CeleryMetricsCollector(config, self.celery)

    def test_correct_driver(self):
        self.redis.scan_iter.return_value = []

        assert CeleryMetricsCollector(config, self.celery) is not None

    def test_queues_empty(self):
        self.redis.scan_iter.return_value = [b"unacked", b"unacked_index"]

        collector = CeleryMetricsCollector(config, self.celery)
        assert collector.queues == set()

    def test_collect_empty_queue(self):
        config.dyno, config.dyno_name, config.dyno_num = "worker.1", "worker", 1
        self.redis.scan_iter.return_value = [b"foo"]
        self.redis.lindex.return_value = None

        collector = CeleryMetricsCollector(config, self.celery)
        metrics: List[Metric] = collector.collect()
        assert len(metrics) == 1
        assert metrics[0].value == 0
        assert metrics[0].queue_name == "foo"

    def test_collect_missing_published_at(self):
        config.dyno, config.dyno_name, config.dyno_num = "worker.1", "worker", 1
        self.redis.scan_iter.return_value = [b"foo"]
        self.redis.lindex.return_value = bytes(json.dumps({"properties": {}}), "utf-8")

        collector = CeleryMetricsCollector(config, self.celery)
        assert len(collector.collect()) == 0

    def test_collect_response_error(self):
        config.dyno, config.dyno_name, config.dyno_num = "worker.1", "worker", 1
        self.redis.scan_iter.return_value = [b"foo"]
        self.redis.lindex.side_effect = redis.exceptions.ResponseError

        collector = CeleryMetricsCollector(config, self.celery)
        with self.assertLogs("judoscale") as captured:
            metrics = collector.collect()
            assert len(metrics) == 1
            assert metrics[0].value == 0
            assert metrics[0].queue_name == "foo"
            message = captured.records[0].getMessage()
            assert message == "Unable to get a task from queue: foo"

    def test_collect(self):
        now = time.time()
        config.dyno, config.dyno_name, config.dyno_num = "worker.1", "worker", 1
        self.redis.scan_iter.return_value = [b"foo", b"bar"]
        self.redis.lindex.return_value = bytes(
            json.dumps({"properties": {"published_at": now}}), "utf-8"
        )

        collector = CeleryMetricsCollector(config, self.celery)
        assert len(collector.collect()) == 2


if __name__ == "__main__":
    unittest.main()
