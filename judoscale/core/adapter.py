from dataclasses import asdict, dataclass
from importlib import metadata
from typing import Optional

from judoscale.core.metrics_collectors import Collector

JUDOSCALE_VERSION = metadata.version("judoscale")


@dataclass
class AdapterInfo:
    """Information about the adapter"""

    runtime_version: str
    adapter_version: str = JUDOSCALE_VERSION


@dataclass
class Adapter:
    """Adapter information and optional metrics collector"""

    identifier: str
    adapter_info: AdapterInfo
    metrics_collector: Optional[Collector] = None

    @property
    def as_tuple(self):
        info = asdict(self.adapter_info)
        if self.metrics_collector is not None:
            # Let the collector contribute adapter-scoped fields (broker
            # stats, etc.) computed during its most recent collect() cycle.
            extra = getattr(self.metrics_collector, "report_metadata", None) or {}
            info.update(extra)
        return (self.identifier, info)
