from abc import ABC, abstractmethod
from typing import List

from judoscale.core.metric import Metric
from judoscale.core.metrics_store import MetricsStore


class MetricsCollector(ABC):
    @abstractmethod
    def collect(self) -> List[Metric]:
        return []


class WebMetricsCollector(MetricsCollector):
    def __init__(self):
        self.store = MetricsStore()
        super().__init__()

    def collect(self) -> List[Metric]:
        return self.store.flush()
