from typing import List, Protocol

from judoscale.core.config import Config
from judoscale.core.metric import Metric
from judoscale.core.metrics_store import MetricsStore


class Collector(Protocol):
    def collect(self) -> List[Metric]:
        ...

    @property
    def should_collect(self) -> bool:
        ...


class MetricsCollector:
    def __init__(self, config: Config):
        self.config = config

    @property
    def should_collect(self) -> bool:
        return True


class WebMetricsCollector(MetricsCollector):
    def __init__(self, config: Config):
        self.store = MetricsStore()
        super().__init__(config=config)

    @property
    def should_collect(self):
        return self.config.dyno_name == "web"

    def add(self, metric: Metric):
        """
        Add metric to the store if it should be collected.
        """
        if self.should_collect:
            self.store.add(metric)

    def collect(self) -> List[Metric]:
        """
        Return all metrics in the store and clear the store.
        """
        return self.store.flush()


class JobMetricsCollector(MetricsCollector):
    def __init__(self, config: Config):
        super().__init__(config=config)

    @property
    def should_collect(self):
        return self.config.dyno_num == 1
