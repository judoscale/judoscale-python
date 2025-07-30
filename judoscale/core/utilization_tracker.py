import os
import threading
import time

from judoscale.core.config import Config, config
from judoscale.core.logger import logger
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import WebMetricsCollector


class UtilizationTracker:
    """

    """

    def __init__(self, config: Config):
        self.config = config
        self.collector = None
        self._thread = None
        self._running = False
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
        logger.info(f"-> utilization #{self.pid}: incr")

    def decr(self):
        logger.info(f"-> utilization #{self.pid}: decr")

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
        # if not self.config.utilization_enabled:
        #     logger.info("Utilization tracker not enabled")
        #     return
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
        logger.info(f"-> utilization #{self.pid}: track current state")
        pass


utilization_tracker = UtilizationTracker(config=config)
