from importlib import metadata
from typing import Mapping

from judoscale.core.adapter import Adapter, AdapterInfo
from judoscale.core.config import config as judoconfig
from judoscale.core.logger import logger
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import WebMetricsCollector
from judoscale.core.reporter import reporter


class RequestQueueTimeMiddleware:
    """Generic middleware class for reporting request queue time metrics to Judoscale"""

    def __init__(self, app, extra_config: Mapping = {}, **kwargs):
        self.app = app
        judoconfig.update(extra_config)

        if not judoconfig.is_enabled:
            logger.info("Not activated - no API URL provivded")
            return

        self.collector = WebMetricsCollector(judoconfig)
        adapter = Adapter(
            identifier=f"judoscale-{self.platform}",
            adapter_info=AdapterInfo(platform_version=metadata.version(self.platform)),
            metrics_collector=self.collector,
        )
        reporter.add_adapter(adapter)
        reporter.ensure_running()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        if judoconfig.is_enabled:
            for header, value in scope["headers"]:
                if header.lower() == b"x-request-start":
                    request_start = value.decode()
                    if metric := Metric.for_web(request_start):
                        self.collector.add(metric)
                    break

            reporter.ensure_running()

        await self.app(scope, receive, send)


class StarletteRequestQueueTimeMiddleware(RequestQueueTimeMiddleware):
    """Starlette middleware for reporting request queue time metrics to Judoscale"""

    platform = "starlette"


class FastAPIRequestQueueTimeMiddleware(RequestQueueTimeMiddleware):
    """FastAPI middleware for reporting request queue time metrics to Judoscale"""

    platform = "fastapi"


class QuartRequestQueueTimeMiddleware(RequestQueueTimeMiddleware):
    """Quart middleware for reporting request queue time metrics to Judoscale"""

    platform = "quart"
