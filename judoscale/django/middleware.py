from judoscale.core.metric import RequestMetrics
from judoscale.core.metrics_store import metrics_store
from judoscale.core.reporter import reporter


class RequestQueueTimeMiddleware:
    """Django middleware for query metrics report"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_start_header = request.META.get("HTTP_X_REQUEST_START", "")

        request_metric = RequestMetrics(request_start_header)
        metric = request_metric.get_queue_time_metric_from_header()
        if metric:
            metrics_store.add(metric)
        reporter.ensure_running()

        return self.get_response(request)
