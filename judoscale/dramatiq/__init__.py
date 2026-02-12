from importlib import metadata
from typing import Mapping

from dramatiq import Broker

from judoscale.core.adapter import Adapter, AdapterInfo
from judoscale.core.config import config as judoconfig
from judoscale.core.logger import logger
from judoscale.core.reporter import reporter
from judoscale.dramatiq.collector import DramatiqMetricsCollector


def judoscale_dramatiq(broker: Broker, extra_config: Mapping = {}) -> None:
    judoconfig.update(extra_config)

    if not judoconfig.is_enabled:
        logger.info("Not activated - no API URL provided")
        return

    collector = DramatiqMetricsCollector(config=judoconfig, broker=broker)
    adapter = Adapter(
        identifier="judoscale-dramatiq",
        adapter_info=AdapterInfo(runtime_version=metadata.version("dramatiq")),
        metrics_collector=collector,
    )

    reporter.add_adapter(adapter)
    reporter.ensure_running()
