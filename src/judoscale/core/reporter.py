import threading
import time
import logging
import os
from judoscale.core.config import config
from judoscale.core.metrics_store import metrics_store
from judoscale.core.adapter_api_client import api_client

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
            if self._thread:
                    self._thread, self._thread.is_alive()))
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
            logger.info(f"Thread is {self._thread}")
            logger.info("Thread is {}".format(self._thread.is_alive()))
            self._report_metrics()
            time.sleep(config.report_interval_seconds)

            if self._stopevent.is_set():
                break

        print(f"{self.get_pid} reports completed before exiting.")

    def get_metrics(self):
        return metrics_store.store

    def _report_metrics(self):
        metrics = metrics_store.flush()
        api_client.post_report(self._build_report(metrics))

    def _build_report(self, metrics):
        metric_to_list = lambda m: [
            round(m.datetime.timestamp()),
            round(m.value, 2),
            m.measurement,
            m.queue_name,
        ]

        return {
            "dyno": config.dyno,
            "pid": self.get_pid,
            "config": config.for_report(),
            "metrics": list(map(metric_to_list, metrics)),
        }


import signal
reporter = Reporter()
signal.signal(signal.SIGTERM, reporter.signal_handler)
