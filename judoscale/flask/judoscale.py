import time
from importlib import metadata
from typing import Optional

from flask import Flask, request, g

from judoscale.core.adapter import Adapter, AdapterInfo
from judoscale.core.config import config as judoconfig
from judoscale.core.logger import logger
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import WebMetricsCollector
from judoscale.core.reporter import reporter
from judoscale.core.utilization_tracker import utilization_tracker


def store_queue_time_metric(collector: WebMetricsCollector):
    def inner():
        request_start_header = request.headers.get("x-request-start", "")
        if metric := Metric.for_web(request_start_header):
            collector.add(metric)
        reporter.ensure_running()
        return None

    return inner

def initialize_app_time_metric():
    g.judoscale_app_start_time = time.monotonic()
    return None

def store_app_time_metric(collector: WebMetricsCollector):
    def inner(response):
        collector.add(Metric.for_web_app_time(start=g.judoscale_app_start_time))
        return response

    return inner

def start_utilization_request_tracking():
    utilization_tracker.ensure_running()
    utilization_tracker.incr()
    return None

def finish_utilization_request_tracking(exception):
    utilization_tracker.decr()

class Judoscale:
    def __init__(self, app: Optional[Flask] = None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        judoconfig.update(app.config.get("JUDOSCALE", {}))

        if not judoconfig.is_enabled:
            logger.info("Not activated - no API URL provided")
            return

        collector = WebMetricsCollector(judoconfig)
        adapter = Adapter(
            identifier="judoscale-flask",
            adapter_info=AdapterInfo(platform_version=metadata.version("flask")),
            metrics_collector=collector,
        )
        reporter.add_adapter(adapter)
        reporter.ensure_running()

        if judoconfig.utilization_enabled:
            app.before_request(start_utilization_request_tracking)
        app.before_request(store_queue_time_metric(collector))
        app.before_request(initialize_app_time_metric)
        app.after_request(store_app_time_metric(collector))
        if judoconfig.utilization_enabled:
            # `teardown_request` is more commonly used to cleanup resources, regardless
            # of success/exception response, and runs later than `after_request`.
            app.teardown_request(finish_utilization_request_tracking)
