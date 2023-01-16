from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import WebMetricsCollector
from judoscale.core.reporter import reporter


class RequestQueueTimeMiddleware:
    """Django middleware for query metrics report"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_start_header = request.META.get("HTTP_X_REQUEST_START", "")

        if metric := Metric.for_web(request_start_header):
            if collector := reporter.find_collector(WebMetricsCollector):
                collector.store.add(metric)
        reporter.ensure_running()

        return self.get_response(request)
