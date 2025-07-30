import time
from importlib import metadata
from contextlib import contextmanager

from judoscale.core.adapter import Adapter, AdapterInfo
from judoscale.core.config import config as judoconfig
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import WebMetricsCollector
from judoscale.core.reporter import reporter
from judoscale.core.utilization_tracker import utilization_tracker


class RequestQueueTimeMiddleware:
    """Django middleware for query metrics report"""

    def __init__(self, get_response):
        self.get_response = get_response
        self.collector = WebMetricsCollector(judoconfig)
        adapter = Adapter(
            identifier="judoscale-django",
            adapter_info=AdapterInfo(platform_version=metadata.version("django")),
            metrics_collector=self.collector,
        )
        reporter.add_adapter(adapter)

    def __call__(self, request):
        with self.track_utilization():
            request_start_header = request.META.get("HTTP_X_REQUEST_START", "")

            if metric := Metric.for_web(request_start_header):
                self.collector.add(metric)
            reporter.ensure_running()

            start = time.monotonic()
            response = self.get_response(request)
            self.collector.add(Metric.for_web_app_time(start=start))

            return response

    @contextmanager
    def track_utilization(self):
        try:
            if judoconfig.utilization_enabled:
                utilization_tracker.ensure_running()
                utilization_tracker.incr()

            yield
        finally:
            if judoconfig.utilization_enabled:
                utilization_tracker.decr()
