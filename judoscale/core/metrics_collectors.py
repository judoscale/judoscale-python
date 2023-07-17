from typing import List, Protocol, Set

from judoscale.core.config import Config
from judoscale.core.logger import logger
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
        return self.config.is_enabled


class WebMetricsCollector(MetricsCollector):
    def __init__(self, config: Config):
        self.store = MetricsStore()
        super().__init__(config=config)

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
    """
    Base class for job metrics collectors.
    This class is not meant to be instantiated directly.
    """

    def __init__(self, config: Config):
        super().__init__(config=config)

    @property
    def adapter_config(self):
        raise NotImplementedError("Implement `adapter_config` in a subclass.")

    @property
    def _queues(self) -> List[str]:
        return list()

    @property
    def queues(self) -> Set[str]:
        if configured_queues := self.adapter_config["QUEUES"]:
            return self.limit_max_queues(configured_queues)
        else:
            return self.limit_max_queues(self._queues)

    @property
    def should_collect(self):
        return (
            super().should_collect
            and self.adapter_config["ENABLED"]
            and not self.config["RUNTIME_CONTAINER"].is_redundant_instance
        )

    def limit_max_queues(self, queues: List[str]) -> Set[str]:
        """
        Limit the number of queues to collect metrics for.
        """

        max_queues = self.adapter_config["MAX_QUEUES"]

        if len(queues) > max_queues:
            logger.warning(
                f"{self.__class__.__name__} reporting only {max_queues} queues max, "
                f"skipping the rest ({len(queues) - max_queues})."
            )

        return set(sorted(queues, key=lambda q: len(q))[:max_queues])
