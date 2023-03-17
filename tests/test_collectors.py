import json
import time
from datetime import datetime, timedelta
from typing import List
from unittest.mock import Mock

import redis.exceptions
import rq.utils as rq_utils
from pytest import approx, fixture, raises
from rq import Queue

from judoscale.celery.collector import CeleryMetricsCollector
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import JobMetricsCollector, WebMetricsCollector
from judoscale.rq.collector import RQMetricsCollector


@fixture
def celery():
    redis = Mock()
    redis.configure_mock(**{"info.return_value": {"redis_version": "6.2.7"}})
    celery = Mock()
    connection = Mock(transport=Mock(driver_name="redis"))
    connection.configure_mock(**{"channel.return_value": Mock(client=redis)})
    celery.configure_mock(**{"connection_for_read.return_value": connection})
    return celery


class TestWebMetricsCollector:
    def test_should_collect(self, web_all):
        assert WebMetricsCollector(web_all).should_collect

    def test_should_not_collect(self, worker_all):
        assert not WebMetricsCollector(worker_all).should_collect

    def test_add(self, web_all):
        collector = WebMetricsCollector(web_all)
        metric = Metric.for_web(f"t={time.time():.3f}")
        collector.add(metric)
        assert collector.store.store == [metric]

    def test_collect(self, web_all):
        collector = WebMetricsCollector(web_all)
        metric = Metric.for_web(f"t={time.time():.3f}")
        collector.add(metric)
        assert collector.collect() == [metric]
        assert collector.store.store == []


class TestJobMetricsCollector:
    def test_should_collect_web(self, web_1):
        assert JobMetricsCollector(web_1).should_collect

    def test_should_not_collect_web(self, heroku_web_2):
        assert not JobMetricsCollector(heroku_web_2).should_collect

    def test_should_collect_worker(self, worker_1):
        assert JobMetricsCollector(worker_1).should_collect

    def test_should_not_collect_worker(self, heroku_worker_2):
        assert not JobMetricsCollector(heroku_worker_2).should_collect


class TestCeleryMetricsCollector:
    def test_incorrect_driver(self, worker_1, celery):
        celery.connection_for_read().transport.driver_name = "not_redis"
        with raises(NotImplementedError):
            CeleryMetricsCollector(worker_1, celery)

    def test_correct_driver(self, worker_1, celery):
        celery.connection_for_read().channel().client.scan_iter.return_value = []
        assert CeleryMetricsCollector(worker_1, celery) is not None

    def test_incorrect_redis_server_version(self, worker_1, celery):
        celery.connection_for_read().channel().client.info.return_value = {
            "redis_version": "5.0.14"
        }
        with raises(RuntimeError, match="Unsupported Redis server version"):
            CeleryMetricsCollector(worker_1, celery)

    def test_queues_empty(self, heroku_worker_1, celery):
        celery.connection_for_read().channel().client.scan_iter.return_value = [
            b"unacked",
            b"unacked_index",
        ]
        collector = CeleryMetricsCollector(heroku_worker_1, celery)
        assert collector.queues == set()

    def test_collect_empty_queue(self, worker_1, celery):
        celery.connection_for_read().channel().client.scan_iter.return_value = [b"foo"]
        celery.connection_for_read().channel().client.lindex.return_value = None

        collector = CeleryMetricsCollector(worker_1, celery)
        metrics: List[Metric] = collector.collect()
        assert len(metrics) == 1
        assert metrics[0].value == approx(0, abs=1)
        assert metrics[0].queue_name == "foo"

    def test_collect_missing_published_at(self, worker_1, celery):
        celery.connection_for_read().channel().client.scan_iter.return_value = [b"foo"]
        celery.connection_for_read().channel().client.lindex.return_value = bytes(
            json.dumps({"properties": {}}), "utf-8"
        )

        collector = CeleryMetricsCollector(worker_1, celery)
        assert len(collector.collect()) == 0

    def test_collect_response_error(self, worker_1, celery, caplog):
        celery.connection_for_read().channel().client.scan_iter.return_value = [b"foo"]
        celery.connection_for_read().channel().client.lindex.side_effect = (
            redis.exceptions.ResponseError
        )

        collector = CeleryMetricsCollector(worker_1, celery)
        metrics = collector.collect()
        assert len(metrics) == 1
        assert metrics[0].value == approx(0, abs=1)
        assert metrics[0].queue_name == "foo"
        assert "Unable to get a task from queue: foo" in caplog.messages

    def test_collect(self, worker_1, celery):
        now = time.time()
        celery.connection_for_read().channel().client.scan_iter.return_value = [
            b"foo",
            b"bar",
        ]
        celery.connection_for_read().channel().client.lindex.return_value = bytes(
            json.dumps({"properties": {"published_at": now}}), "utf-8"
        )

        collector = CeleryMetricsCollector(worker_1, celery)
        assert len(collector.collect()) == 2


class TestRQMetricsCollector:
    def test_no_queues(self, worker_1):
        redis = Mock()
        redis.smembers.return_value = []
        collector = RQMetricsCollector(worker_1, redis)
        assert collector.queues == []

    def test_queues(self, worker_1):
        redis = Mock()
        redis.smembers.return_value = [b"rq:queue:foo"]

        collector = RQMetricsCollector(worker_1, redis)
        assert collector.queues == [Queue("foo", connection=redis)]

    def test_collect_empty_queue(self, worker_1):
        redis = Mock()
        redis.smembers.return_value = [b"rq:queue:foo"]
        redis.lrange.return_value = []

        collector = RQMetricsCollector(worker_1, redis)
        metrics: List[Metric] = collector.collect()
        assert len(metrics) == 1
        assert metrics[0].value == approx(0, abs=1)
        assert metrics[0].queue_name == "foo"

    def test_collect_response_error(self, worker_1, caplog):
        redis = Mock()
        redis.smembers.return_value = [b"rq:queue:foo"]
        redis.lrange.side_effect = redis.exceptions.ResponseError

        collector = RQMetricsCollector(worker_1, redis)
        metrics = collector.collect()
        assert len(metrics) == 1
        assert metrics[0].value == approx(0, abs=1)
        assert metrics[0].queue_name == "foo"
        assert "Unable to get a task from queue: foo" in caplog.messages

    def test_collect(self, worker_1):
        redis = Mock()
        redis.smembers.return_value = [b"rq:queue:foo"]
        redis.lrange.return_value = [b"123"]
        redis.hgetall.return_value = {
            # Simulate a job that was enqueued 1 minute ago
            b"enqueued_at": rq_utils.utcformat(
                datetime.utcnow() - timedelta(minutes=1)
            ).encode(),
            # Job origin has to match the queue name
            b"origin": b"foo",
            # Job data key is required but can be empty
            b"data": b"",
        }

        collector = RQMetricsCollector(worker_1, redis)
        metrics: List[Metric] = collector.collect()
        assert len(metrics) == 1
        assert metrics[0].value == approx(60000, abs=100)
        assert metrics[0].queue_name == "foo"
