from flask import request

from judoscale.core.config import config as judoconfig
from judoscale.core.metric import RequestMetrics
from judoscale.core.metrics_store import metrics_store
from judoscale.core.reporter import reporter


def store_request_metrics():
    request_start_header = request.headers.get("x-request-start", "")
    request_metric = RequestMetrics(request_start_header)
    metric = request_metric.get_queue_time_metric_from_header()
    if metric:
        metrics_store.add(metric)
    reporter.ensure_running()
    return None


class Judoscale:
    def __init__(self, app=None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        judoconfig.merge(app.config.get("JUDOSCALE", {}))
        reporter.ensure_running()
        app.before_request(store_request_metrics)
