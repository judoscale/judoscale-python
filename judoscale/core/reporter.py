import logging
import os
import signal
import threading
import time

from judoscale.core.adapter_api_client import api_client
from judoscale.core.config import config
from judoscale.core.metrics_store import metrics_store

logger = logging.getLogger(__name__)


class Reporter:
    def __init__(self):
        self._thread = None
        self._running = False
        self._stopevent = threading.Event()

    def start(self):
        pid = self.get_pid
        logger.info(f"Starting reporter for process {pid}")
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        self._running = True

    def ensure_running(self):
        try:
            if not self.is_running:
                return self.start()
        except Exception as e:
            logger.warning(f"{e.args} - No reporter has initiated")
            pass

    def signal_handler(self, signum, frame):
        self._stopevent.set()
        self._running = False

    @property
    def is_running(self):
        if self._thread and self._thread.is_alive():
            self._running = True
        else:
            self._running = False
        return self._running

    @property
    def get_pid(self):
        return os.getpid()

    def _run_loop(self):
        while self.is_running:
            self._report_metrics()
            time.sleep(config.report_interval_seconds)

            if self._stopevent.is_set():
                break

        logger.info(f"{self.get_pid} reports completed before exiting.")

    def get_metrics(self):
        return metrics_store.store

    def _report_metrics(self):
        metrics = metrics_store.flush()
        api_client.post_report(self._build_report(metrics))

    def _metric_to_list(self, metric):
        return [
            round(metric.datetime.timestamp()),
            round(metric.value, 2),
            metric.measurement,
            metric.queue_name,
        ]

    def _build_report(self, metrics):
        return {
            "dyno": config.dyno,
            "pid": self.get_pid,
            "config": config.for_report(),
            "metrics": list(map(self._metric_to_list, metrics)),
        }


reporter = Reporter()
signal.signal(signal.SIGTERM, reporter.signal_handler)
