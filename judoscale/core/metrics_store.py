import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MetricsStore:
    # max_flush_interval exists to prevent collecting metrics in memory if they
    # are never being flushed (if the reporter has failed for some reason).
    def __init__(self, max_flush_interval=60):
        self.store = []
        self.max_flush_interval = max_flush_interval
        self.last_flush_time = datetime.now()

    def add(self, metric):
        if self.last_flush_time > datetime.now() - timedelta(
            seconds=self.max_flush_interval
        ):
            self.store.append(metric)
        else:
            logger.debug("Max flush interval exceeded - Not adding metric to store.")

    def flush(self):
        self.last_flush_time = datetime.now()
        result = []
        # This operation needs to be atomic since the main thread is appending to the store
        while metric := self._pop():
            result.append(metric)

        return result

    def _pop(self):
        try:
            return self.store.pop() if self.store else None
        except IndexError:
            return None


metrics_store = MetricsStore()
