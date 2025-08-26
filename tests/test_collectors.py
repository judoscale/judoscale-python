import json
import time
from datetime import datetime, timedelta, timezone
from typing import List
from unittest.mock import Mock

import redis.exceptions
import rq.utils as rq_utils
from pytest import approx, fixture, raises

from judoscale.celery.collector import CeleryMetricsCollector
from judoscale.core.metric import Metric
from judoscale.core.metrics_store import MetricsStore
from judoscale.core.metrics_collectors import JobMetricsCollector, WebMetricsCollector
from judoscale.core.utilization_tracker import utilization_tracker
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


@fixture(autouse=True)
def run_before_and_after_tests():
    yield
    utilization_tracker.stop()


class TestWebMetricsCollector:
    def test_should_collect_web(self, web_all):
        assert WebMetricsCollector(
            web_all,
        ).should_collect

    def test_should_collect_worker(self, worker_all):
        assert WebMetricsCollector(worker_all, MetricsStore()).should_collect

    def test_add(self, web_all):
        collector = WebMetricsCollector(web_all, MetricsStore())
        metric = Metric.for_web(f"t={time.time():.3f}")
        collector.add(metric)
        assert collector.store.store == [metric]

    def test_collect(self, web_all):
        collector = WebMetricsCollector(web_all, MetricsStore())
        metric = Metric.for_web(f"t={time.time():.3f}")
        collector.add(metric)
        assert collector.collect() == [metric]
        assert collector.store.store == []

    def test_collect_with_utilization_tracker(self, web_all):
        utilization_tracker.start()
        collector = WebMetricsCollector(web_all, MetricsStore())

        time.sleep(0.001)
        collected_metrics = collector.collect()
        assert len(collected_metrics) == 1
        assert collected_metrics[0].measurement == "up"
        assert collected_metrics[0].value == 0
        assert collector.store.store == []

        utilization_tracker.incr()
        time.sleep(0.001)

        collected_metrics = collector.collect()
        assert len(collected_metrics) == 1
        assert collected_metrics[0].measurement == "up"
        assert collected_metrics[0].value > 0


class TestJobMetricsCollector:
    def test_raises_not_implemented_error(self, web_1):
        with raises(
            NotImplementedError,
            match="Implement `adapter_config` in a subclass.",
        ):
            assert JobMetricsCollector(web_1).should_collect

    def test_should_collect_web(self, web_1, monkeypatch):
        monkeypatch.setattr(JobMetricsCollector, "adapter_config", {"ENABLED": True})
        assert JobMetricsCollector(web_1).should_collect

    def test_should_collect_worker(self, worker_1, monkeypatch):
        monkeypatch.setattr(JobMetricsCollector, "adapter_config", {"ENABLED": True})
        assert JobMetricsCollector(worker_1).should_collect

    def test_should_not_collect_worker_2(self, heroku_worker_2, monkeypatch):
        monkeypatch.setattr(JobMetricsCollector, "adapter_config", {"ENABLED": True})
        assert not JobMetricsCollector(heroku_worker_2).should_collect

    def test_limit_max_queues_under_limit(self, web_1, monkeypatch):
        monkeypatch.setattr(JobMetricsCollector, "adapter_config", {"MAX_QUEUES": 2})
        collector = JobMetricsCollector(web_1)
        assert collector.limit_max_queues(["default", "high"]) == {"high", "default"}

    def test_limit_max_queues_over_limit(self, web_1, monkeypatch):
        monkeypatch.setattr(JobMetricsCollector, "adapter_config", {"MAX_QUEUES": 1})
        collector = JobMetricsCollector(web_1)
        assert collector.limit_max_queues(["default", "high"]) == {"high"}

    def test_queues_with_user_queues(self, web_1, monkeypatch):
        monkeypatch.setattr(
            JobMetricsCollector,
            "adapter_config",
            {"QUEUES": ["foo", "bar"], "MAX_QUEUES": 20},
        )
        collector = JobMetricsCollector(web_1)
        assert collector.queues == {"foo", "bar"}

    def test_queues_with_user_queues_and_max_queues(self, web_1, monkeypatch):
        monkeypatch.setattr(
            JobMetricsCollector,
            "adapter_config",
            {"QUEUES": ["three", "two", "one"], "MAX_QUEUES": 2},
        )
        collector = JobMetricsCollector(web_1)
        assert collector.queues == {"one", "two"}

    def test_queues_without_user_queues_with_max_queues(self, web_1, monkeypatch):
        monkeypatch.setattr(
            JobMetricsCollector,
            "adapter_config",
            {"QUEUES": [], "MAX_QUEUES": 2},
        )
        monkeypatch.setattr(JobMetricsCollector, "_queues", ["queues", "from", "redis"])
        collector = JobMetricsCollector(web_1)
        assert collector.queues == {"from", "redis"}


class TestCeleryMetricsCollector:
    def test_adapter_config(self, render_worker, celery):
        celery.connection_for_read().channel().client.scan_iter.return_value = []
        render_worker["CELERY"] = {
            "ENABLED": False,
            "QUEUES": ["foo", "bar"],
        }
        collector = CeleryMetricsCollector(render_worker, celery)
        assert collector.adapter_config == {
            "ENABLED": False,
            "QUEUES": ["foo", "bar"],
            "MAX_QUEUES": 20,
            "TRACK_BUSY_JOBS": False,
        }

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

    def test_removing_various_celery_queues(self, heroku_worker_1, celery):
        celery.connection_for_read().channel().client.scan_iter.return_value = [
            b"unacked",
            b"unacked_index",
            b"_kombu.binding.celeryev",
            b"e752fa70-f772-3c04-b05d-79b2a79ce766.reply.celery.pidbox",
            b"user_queue",
        ]
        collector = CeleryMetricsCollector(heroku_worker_1, celery)
        assert collector.queues == {"user_queue"}

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
            json.dumps({"id": "123abc", "properties": {}}), "utf-8"
        )

        collector = CeleryMetricsCollector(worker_1, celery)
        assert len(collector.collect()) == 0

    def test_collect_missing_published_at_and_id(self, worker_1, celery):
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

    def test_collect_no_properties(self, worker_1, celery):
        celery.connection_for_read().channel().client.scan_iter.return_value = [
            b"foo",
        ]
        celery.connection_for_read().channel().client.lindex.return_value = bytes(
            json.dumps({"id": "123abc"}), "utf-8"
        )

        collector = CeleryMetricsCollector(worker_1, celery)
        assert len(collector.collect()) == 0

    def test_collect(self, worker_1, celery):
        now = time.time()
        celery.connection_for_read().channel().client.scan_iter.return_value = [
            b"foo",
            b"bar",
        ]
        celery.connection_for_read().channel().client.lindex.return_value = bytes(
            json.dumps({"id": "123abc", "properties": {"published_at": now}}), "utf-8"
        )

        collector = CeleryMetricsCollector(worker_1, celery)
        assert len(collector.collect()) == 2

    def test_collect_with_busy_jobs(self, worker_1, celery, monkeypatch):
        now = time.time()

        inspect = Mock()
        inspect.active.return_value = {
            "some_worker": [{"name": "a_task", "delivery_info": {"routing_key": "foo"}}]
        }

        monkeypatch.setattr(celery.control, "inspect", lambda connection: inspect)
        celery.connection_for_read().channel().client.scan_iter.return_value = [
            b"foo",
        ]
        celery.connection_for_read().channel().client.lindex.return_value = bytes(
            json.dumps({"properties": {"published_at": now - 60}}), "utf-8"
        )

        worker_1["CELERY"] = {"TRACK_BUSY_JOBS": True}
        collector = CeleryMetricsCollector(worker_1, celery)
        metrics = collector.collect()

        assert len(metrics) == 2

        assert metrics[0].measurement == "busy"
        assert metrics[0].queue_name == "foo"
        assert metrics[0].value == 1

        assert metrics[1].measurement == "qt"
        assert metrics[1].queue_name == "foo"
        assert metrics[1].value == approx(60000, abs=100)

    def test_collect_with_busy_jobs_and_user_defined_queues(
        self, worker_1, celery, monkeypatch
    ):
        now = time.time()

        inspect = Mock()
        inspect.active.return_value = {
            "some_worker": [{"name": "a_task", "delivery_info": {"routing_key": "foo"}}]
        }

        monkeypatch.setattr(celery.control, "inspect", lambda connection: inspect)
        celery.connection_for_read().channel().client.scan_iter.return_value = [
            b"foo",
        ]

        def mock_lindex(queue, _):
            return {
                "bar": {},
                "foo": bytes(
                    json.dumps({"properties": {"published_at": now - 60}}), "utf-8"
                ),
            }[queue]

        monkeypatch.setattr(
            celery.connection_for_read().channel().client, "lindex", mock_lindex
        )

        worker_1["CELERY"] = {"QUEUES": ["foo", "bar"], "TRACK_BUSY_JOBS": True}
        collector = CeleryMetricsCollector(worker_1, celery)
        metrics = collector.collect()

        assert len(metrics) == 4
        metrics = sorted(metrics, key=lambda m: m.queue_name)
        metrics = sorted(metrics, key=lambda m: m.measurement)

        assert metrics[0].measurement == "busy"
        assert metrics[0].queue_name == "bar"
        assert metrics[0].value == 0

        assert metrics[1].measurement == "busy"
        assert metrics[1].queue_name == "foo"
        assert metrics[1].value == 1

        assert metrics[2].measurement == "qt"
        assert metrics[2].queue_name == "bar"
        assert metrics[2].value == 0

        assert metrics[3].measurement == "qt"
        assert metrics[3].queue_name == "foo"
        assert metrics[3].value == approx(60000, abs=100)


class TestRQMetricsCollector:
    def test_adapter_config(self, render_worker):
        render_worker["RQ"] = {
            "ENABLED": False,
            "QUEUES": ["foo", "bar"],
        }
        collector = RQMetricsCollector(render_worker, Mock())
        assert collector.adapter_config == {
            "ENABLED": False,
            "QUEUES": ["foo", "bar"],
            "MAX_QUEUES": 20,
            "TRACK_BUSY_JOBS": False,
        }

    def test_no_queues(self, worker_1):
        redis = Mock()
        redis.smembers.return_value = []
        collector = RQMetricsCollector(worker_1, redis)
        assert collector.queues == set()

    def test_queues(self, worker_1):
        redis = Mock()
        redis.smembers.return_value = [b"rq:queue:foo"]

        collector = RQMetricsCollector(worker_1, redis)
        assert collector.queues == {"foo"}

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
                datetime.now(tz=timezone.utc).replace(tzinfo=None)
                - timedelta(minutes=1)
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

    def test_collect_with_busy_job_tracking(self, worker_1, monkeypatch):
        monkeypatch.setattr("rq.registry.StartedJobRegistry.count", 1)
        redis = Mock()
        redis.smembers.return_value = [b"rq:queue:foo"]
        redis.lrange.return_value = [b"123"]
        redis.hgetall.return_value = {
            # Simulate a job that was enqueued 1 minute ago
            b"enqueued_at": rq_utils.utcformat(
                datetime.now(tz=timezone.utc).replace(tzinfo=None)
                - timedelta(minutes=1)
            ).encode(),
            # Job origin has to match the queue name
            b"origin": b"foo",
            # Job data key is required but can be empty
            b"data": b"",
        }

        worker_1["RQ"] = {"TRACK_BUSY_JOBS": True}
        collector = RQMetricsCollector(worker_1, redis)
        metrics: List[Metric] = collector.collect()

        assert len(metrics) == 2

        assert metrics[0].measurement == "busy"
        assert metrics[0].queue_name == "foo"
        assert metrics[0].value == 1

        assert metrics[1].measurement == "qt"
        assert metrics[1].queue_name == "foo"
        assert metrics[1].value == approx(60000, abs=100)
