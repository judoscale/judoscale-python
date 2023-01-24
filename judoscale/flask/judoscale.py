from flask import request

from judoscale.core.config import config as judoconfig
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import WebMetricsCollector
from judoscale.core.reporter import reporter


def store_request_metrics(collector: WebMetricsCollector):
    def inner():
        request_start_header = request.headers.get("x-request-start", "")
        if metric := Metric.for_web(request_start_header):
            collector.store.add(metric)
        reporter.ensure_running()
        return None

    return inner


class Judoscale:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        judoconfig.merge(app.config.get("JUDOSCALE", {}))
        collector = WebMetricsCollector()
        reporter.add_collector(collector)
        reporter.ensure_running()
        app.before_request(store_request_metrics(collector))
