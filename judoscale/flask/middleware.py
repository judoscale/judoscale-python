from werkzeug.wrappers import Request

from judoscale.core.metrics_store import metrics_store
from judoscale.core.metric import RequestMetrics
from judoscale.core.reporter import reporter


class RequestQueueTimeMiddleware:
    """ WSGI middleware for query metrics report"""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        request = Request(environ)
        request_start_header = request.environ.get("HTTP_X_REQUEST_START", "")

        request_metric = RequestMetrics(request_start_header)
        metric = request_metric.get_queue_time_metric_from_header()
        if metric:
            metrics_store.add(metric)
        reporter.ensure_running()

        return self.app(environ, start_response)
