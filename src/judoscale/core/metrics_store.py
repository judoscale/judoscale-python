import logging

logger = logging.getLogger(__name__)

class MetricsStore:
    def __init__(self):
        self.store = []

    def add(self, metric):
        self.store.append(metric)

    def flush(self):
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
