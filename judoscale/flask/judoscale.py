from importlib import metadata
from typing import Optional

from flask import Flask, request

from judoscale.core.adapter import Adapter, AdapterInfo
from judoscale.core.config import config as judoconfig
from judoscale.core.logger import logger
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import WebMetricsCollector
from judoscale.core.reporter import reporter


def store_request_metrics(collector: WebMetricsCollector):
    def inner():
        request_start_header = request.headers.get("x-request-start", "")
        if metric := Metric.for_web(request_start_header):
            collector.add(metric)
        reporter.ensure_running()
        return None

    return inner


class Judoscale:
    def __init__(self, app: Optional[Flask] = None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        judoconfig.update(app.config.get("JUDOSCALE", {}))

        if not judoconfig.is_enabled:
            logger.info("Not activated - no API URL provivded")
            return

        collector = WebMetricsCollector(judoconfig)
        adapter = Adapter(
            identifier="judoscale-flask",
            adapter_info=AdapterInfo(platform_version=metadata.version("flask")),
            metrics_collector=collector,
        )
        reporter.add_adapter(adapter)
        reporter.ensure_running()
        app.before_request(store_request_metrics(collector))
