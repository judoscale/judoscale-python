import os
import threading
import time

from judoscale.core.config import Config, config
from judoscale.core.logger import logger
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import WebMetricsCollector


class UtilizationTracker:
    """
    Tracks a count of active requests, incremented / decremented by the request
    middleware, and runs a separate thread that adds a "utilization" metric
    based on the process being currently handling any requests or idle.
    """

    def __init__(self, config: Config):
        self.config = config
        self.collector = None
        self.active_requests = 0
        self._thread = None
        self._running = False
        self._lock = threading.Lock()
        self._stopevent = threading.Event()

    def start(self, collector: WebMetricsCollector):
        self.collector = collector
        self._start()

    def ensure_running(self):
        try:
            if not self.is_running:
                return self._start()
        except Exception as e:
            logger.warning(f"{e.args} - No utilization tracker has initiated")
            pass

    def signal_handler(self, signum, frame):
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

    def _start(self):
        logger.info(f"Starting utilization tracker for process {self.pid}")
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._running = True

    def _run_loop(self):
        while self.is_running:
            time.sleep(self.config.utilization_interval)
            self._track_current_state()

            if self._stopevent.is_set():
                break

    def _track_current_state(self):
        active_processes = 1 if self.active_requests > 0 else 0
        logger.debug(f"-> utilization {self.pid}: track current state: {active_processes}")
        self.collector.add(Metric.for_web_utilization(active_processes))


utilization_tracker = UtilizationTracker(config=config)
