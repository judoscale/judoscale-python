import logging
import time
from datetime import datetime
from unittest.mock import patch, MagicMock

import requests
from pytest import fixture

from judoscale.core.adapter import Adapter, AdapterInfo
from judoscale.core.config import config
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import WebMetricsCollector
from judoscale.core.reporter import Reporter


@fixture
def reporter(heroku_web_1):
    reporter = Reporter(heroku_web_1)
    yield reporter
    reporter.stop()


@fixture(params=["heroku_release_1", "heroku_run_1234", "scalingo_one_off_1234"])
def reporter_in_ephemeral_instance(request):
    reporter = Reporter(request.getfixturevalue(request.param))
    yield reporter
    reporter.stop()


class TestReporter:
    def test_build_report(self, reporter):
        dt = datetime.fromisoformat("2012-12-12T12:12:00+00:00")
        metric = Metric(measurement="test", timestamp=dt.timestamp(), value=123)

        report = reporter._build_report([metric])

        assert sorted(list(report.keys())) == sorted(
            ["adapters", "config", "container", "pid", "metrics", "metadata"]
        )
        assert len(report["metrics"]) == 1
        assert report["metrics"][0] == (1355314320, 123, "test", None)
        assert report["metadata"] == {}

    def test_no_explicit_adapter(self, reporter):
        assert len(reporter.adapters) == 1
        assert reporter.adapters[0].identifier == "judoscale-python"

    def test_add_adapter_no_collector(self, reporter):
        adapter = Adapter(
            identifier="test",
            adapter_info=AdapterInfo(runtime_version="0.0.0"),
            metrics_collector=None,
        )
        reporter.add_adapter(adapter)
        assert adapter in reporter.adapters
        assert reporter.collectors == []

    def test_add_adapter_with_collector(self, reporter):
        adapter = Adapter(
            identifier="test",
            adapter_info=AdapterInfo(runtime_version="0.0.0"),
            metrics_collector=WebMetricsCollector(config),
        )
        reporter.add_adapter(adapter)
        assert adapter in reporter.adapters
        assert reporter.collectors == [adapter.metrics_collector]

    def test_all_metrics_empty(self, reporter):
        assert reporter.all_metrics == []

    def test_all_metrics_not_empty(self, reporter):
        collector_instance_1 = WebMetricsCollector(reporter.config)
        adapter_instance_1 = Adapter(
            identifier="test",
            adapter_info=AdapterInfo(runtime_version="0.0.0"),
            metrics_collector=collector_instance_1,
        )
        collector_instance_2 = WebMetricsCollector(reporter.config)
        adapter_instance_2 = Adapter(
            identifier="test",
            adapter_info=AdapterInfo(runtime_version="0.0.0"),
            metrics_collector=collector_instance_2,
        )
        reporter.add_adapter(adapter_instance_1)
        reporter.add_adapter(adapter_instance_2)
        collector_instance_1.add(Metric(measurement="qt", timestamp=0, value=0))
        collector_instance_2.add(Metric(measurement="qt", timestamp=0, value=0))
        assert len(reporter.all_metrics) == 2

    def test_start_without_api_base_url(self, reporter, caplog):
        reporter.config["API_BASE_URL"] = None
        assert not reporter.config.is_enabled
        reporter.start()
        assert not reporter.is_running

    def test_start(self, reporter):
        assert reporter.config.is_enabled
        reporter.start()
        assert reporter.is_running

    def test_start_in_ephemeral_instance(self, reporter_in_ephemeral_instance, caplog):
        caplog.set_level(logging.INFO, logger="judoscale")

        assert reporter_in_ephemeral_instance.config.is_enabled
        reporter_in_ephemeral_instance.ensure_running()
        assert not reporter_in_ephemeral_instance.is_running

        assert any(
            record.levelname == "INFO"
            and "Reporter not started: in an ephemeral container" in record.message
            for record in caplog.records
        )

    @patch.object(time, "sleep")
    @patch.object(requests, "post")
    def test_retries_transient_errors(
        self, mock_post, mock_sleep, reporter
    ):
        mock_post.side_effect = [
            requests.ConnectionError("Connection refused"),
            MagicMock(status_code=200),
        ]

        reporter._report_metrics()

        assert mock_post.call_count == 2

    @patch.object(time, "sleep")
    @patch.object(requests, "post")
    def test_does_not_retry_non_transient_errors(
        self, mock_post, mock_sleep, reporter
    ):
        mock_post.side_effect = requests.HTTPError("500 Server Error")

        reporter._report_metrics()

        assert mock_post.call_count == 1

    def test_build_report_includes_collector_report_metadata(self, reporter):
        # Subclass so we can swap the property without fighting the descriptor.
        class _CollectorWithExtras(WebMetricsCollector):
            @property
            def report_metadata(self):
                return {"celery-broker": {"connected_clients": 31, "maxclients": 40}}

        collector = _CollectorWithExtras(reporter.config)
        reporter.add_adapter(
            Adapter(
                identifier="judoscale-celery",
                adapter_info=AdapterInfo(runtime_version="5.6.3"),
                metrics_collector=collector,
            )
        )

        report = reporter._build_report([])

        celery_entry = report["adapters"]["judoscale-celery"]
        assert celery_entry["runtime_version"] == "5.6.3"

        assert report["metadata"] == {
            "celery-broker": {"connected_clients": 31, "maxclients": 40}
        }

    def test_build_report_omits_empty_collector_report_metadata(self, reporter):
        collector = WebMetricsCollector(reporter.config)
        reporter.add_adapter(
            Adapter(
                identifier="judoscale-celery",
                adapter_info=AdapterInfo(runtime_version="5.6.3"),
                metrics_collector=collector,
            )
        )

        report = reporter._build_report([])

        celery_entry = report["adapters"]["judoscale-celery"]
        assert celery_entry == {
            "runtime_version": "5.6.3",
            "adapter_version": celery_entry["adapter_version"],
        }
        assert report["metadata"] == {}

    def test_all_metrics_continues_when_one_collector_raises(
        self, reporter, caplog
    ):
        caplog.set_level(logging.ERROR, logger="judoscale")

        failing_collector = WebMetricsCollector(reporter.config)
        failing_collector.collect = MagicMock(side_effect=RuntimeError("boom"))
        reporter.add_adapter(
            Adapter(
                identifier="failing",
                adapter_info=AdapterInfo(runtime_version="0.0.0"),
                metrics_collector=failing_collector,
            )
        )

        healthy_collector = WebMetricsCollector(reporter.config)
        healthy_collector.add(Metric(measurement="qt", timestamp=0, value=0))
        reporter.add_adapter(
            Adapter(
                identifier="healthy",
                adapter_info=AdapterInfo(runtime_version="0.0.0"),
                metrics_collector=healthy_collector,
            )
        )

        metrics = reporter.all_metrics

        assert len(metrics) == 1
        assert any(
            "failed to collect metrics" in record.message
            for record in caplog.records
        )

    @patch.object(time, "sleep")
    def test_run_loop_survives_report_metrics_exception(
        self, mock_sleep, reporter, caplog
    ):
        caplog.set_level(logging.ERROR, logger="judoscale")

        call_count = {"n": 0}

        def fail_first_then_stop():
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise RuntimeError("kaboom")
            reporter._stopevent.set()

        reporter._report_metrics = MagicMock(side_effect=fail_first_then_stop)
        reporter.start()
        reporter._thread.join(timeout=2)

        assert call_count["n"] >= 2
        assert any(
            "Reporter cycle failed" in record.message
            for record in caplog.records
        )
