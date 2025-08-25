import os
import threading
import time

from judoscale.core.logger import logger
from judoscale.core.metric import Metric
from judoscale.core.metrics_store import MetricsStore, metrics_store


class UtilizationTracker:
    """
    Tracks a count of active requests, incremented / decremented by the request
    middleware, and runs a separate thread that adds a "utilization" metric to
    the store, based on the process handling any requests or being idle.

    It pushes metrics directly to the underlying store, the same used by the
    WebMetricsCollector, which are them flushed and included with reports.
    """

    def __init__(self, store: MetricsStore):
        self.store = store
        self.active_requests = 0
        self._thread = None
        self._running = False
        self._lock = threading.Lock()
        self._stopevent = threading.Event()

    def start(self):
        logger.info(f"Starting utilization tracker for process {self.pid}")
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._running = True

    def ensure_running(self):
        try:
            if not self.is_running:
                return self.start()
        except Exception as e:
            logger.warning(f"{e.args} - No utilization tracker has initiated")
            pass

    def stop(self):
        self._stopevent.set()
        self._running = False

    def incr(self):
        logger.debug(f"-> utilization {self.pid}: incr")
        with self._lock:
            self.active_requests = self.active_requests + 1

    def decr(self):
        logger.debug(f"-> utilization {self.pid}: decr")
        with self._lock:
            self.active_requests = self.active_requests - 1

    @property
    def is_running(self):
        if self._thread and self._thread.is_alive():
            self._running = True
        else:
            self._running = False
        return self._running

    @property
    def pid(self) -> int:
        return os.getpid()

    def _run_loop(self):
        while self.is_running:
            # TODO: to be removed with utilization tracker thread implementation.
            time.sleep(1.0)
            self._track_current_state()

            if self._stopevent.is_set():
                break

    def _track_current_state(self):
        active_requests = self.active_requests
        active_processes = 1 if active_requests > 0 else 0
        logger.debug(f"-> utilization {self.pid}: track current state: pu={active_processes} ru={active_requests}")
        self.store.add(Metric.for_web_process_utilization(active_processes))
        self.store.add(Metric.for_web_request_utilization(active_requests))


utilization_tracker = UtilizationTracker(store=metrics_store)
