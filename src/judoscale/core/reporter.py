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
        pid = os.getpid()
        logger.info(f"Starting reporter for process {pid}")
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()

    def stop(self, timeout=None):
        self._stopevent.set()
        self._thread.join(timeout)
        self._running = False

    @property
    def is_running(self):
        return self._running

    def _run_loop(self):
        while self._running:
            self._report_metrics()
            time.sleep(config.report_interval_seconds)

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
            # TODO: Does each thread get its own PID?
            "pid": os.getpid(),
            "config": config.for_report(),
            "metrics": list(map(metric_to_list, metrics)),
        }


reporter = Reporter()
