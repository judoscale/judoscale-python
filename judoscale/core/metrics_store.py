import time
from typing import List, Optional

from judoscale.core.logger import logger
from judoscale.core.metric import Metric


class MetricsStore:
    """
    A thread-safe store for metrics.
    """

    def __init__(self, max_flush_interval: int = 60):
        self.store: List[Metric] = []
        # The max_flush_interval exists to prevent collecting metrics in memory
        # if they are never being flushed (if the reporter has failed for some
        # reason).
        self.max_flush_interval: int = max_flush_interval
        self.last_flush_time: float = time.monotonic()

    def add(self, metric: Metric) -> None:
        """
        Add a metric to the store.

        If the max flush interval has been exceeded, the metric will not be
        added to the store.
        """
        if self.last_flush_time > time.monotonic() - self.max_flush_interval:
            self.store.append(metric)
        else:
            logger.debug("Max flush interval exceeded - Not adding metric to store.")

    def flush(self) -> List[Metric]:
        """
        Return all metrics in the store and clear the store.
        """
        self.last_flush_time = time.monotonic()
        result = []
        # This operation needs to be atomic since the main thread is appending
        # to the store
        while metric := self._pop():
            result.append(metric)

        return result

    def _pop(self) -> Optional[Metric]:
        try:
            return self.store.pop() if self.store else None
        except IndexError:
            return None
