from importlib import metadata
from typing import Mapping

from redis import Redis

from judoscale.core.adapter import Adapter, AdapterInfo
from judoscale.core.config import config as judoconfig
from judoscale.core.logger import logger
from judoscale.core.reporter import reporter
from judoscale.rq.collector import RQMetricsCollector


def judoscale_rq(redis: Redis, extra_config: Mapping = {}) -> None:
    judoconfig.update(extra_config)

    if not judoconfig.is_enabled:
        logger.info("Not activated - no API URL provivded")
        return

    collector = RQMetricsCollector(config=judoconfig, redis=redis)
    adapter = Adapter(
        identifier="judoscale-rq",
        adapter_info=AdapterInfo(platform_version=metadata.version("rq")),
        metrics_collector=collector,
    )

    reporter.add_adapter(adapter)
    reporter.ensure_running()
