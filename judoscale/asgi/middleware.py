from importlib import metadata
from typing import Mapping

from starlette.requests import Request

from judoscale.core.adapter import Adapter, AdapterInfo
from judoscale.core.config import config as judoconfig
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import WebMetricsCollector
from judoscale.core.reporter import reporter


class RequestQueueTimeMiddleware:
    """FastAPI middleware for query metrics report""" ""

    def __init__(self, app, extra_config: Mapping = {}, **kwargs):
        self.app = app
        judoconfig.update(extra_config)
        self.collector = WebMetricsCollector(judoconfig)
        adapter = Adapter(
            identifier="judoscale-fastapi",
            adapter_info=AdapterInfo(platform_version=metadata.version("fastapi")),
            metrics_collector=self.collector,
        )
        reporter.add_adapter(adapter)
        reporter.ensure_running()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        request_start = request.headers.get("x-request-start", "")
        if metric := Metric.for_web(request_start):
            self.collector.add(metric)
        reporter.ensure_running()

        await self.app(scope, receive, send)
