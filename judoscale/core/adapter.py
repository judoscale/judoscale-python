from dataclasses import asdict, dataclass
from importlib import metadata
from typing import Optional

from judoscale.core.metrics_collectors import Collector

JUDOSCALE_VERSION = metadata.version("judoscale")


@dataclass
class AdapterInfo:
    """Information about the adapter"""

    platform_version: str
    adapter_version: str = JUDOSCALE_VERSION


@dataclass
class Adapter:
    """Adapter information and optional metrics collector"""

    identifier: str
    adapter_info: AdapterInfo
    metrics_collector: Optional[Collector] = None

    @property
    def as_tuple(self):
        return (self.identifier, asdict(self.adapter_info))
