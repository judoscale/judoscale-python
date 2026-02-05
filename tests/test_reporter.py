import logging
from datetime import datetime

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


@fixture
def reporter_in_release(heroku_release_1):
    reporter = Reporter(heroku_release_1)
    yield reporter
    reporter.stop()


class TestReporter:
    def test_build_report(self, reporter):
        dt = datetime.fromisoformat("2012-12-12T12:12:00+00:00")
        metric = Metric(measurement="test", timestamp=dt.timestamp(), value=123)

        report = reporter._build_report([metric])

        assert sorted(list(report.keys())) == sorted(
            ["adapters", "config", "container", "pid", "metrics"]
        )
        assert len(report["metrics"]) == 1
        assert report["metrics"][0] == (1355314320, 123, "test", None)

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

    def test_start_in_release(self, reporter_in_release, caplog):
        caplog.set_level(logging.INFO, logger="judoscale")

        assert reporter_in_release.config.is_enabled
        reporter_in_release.ensure_running()
        assert not reporter_in_release.is_running

        for record in caplog.records:
            assert record.levelname == "INFO"
            assert "Reporter not started: in a build process" in record.message
