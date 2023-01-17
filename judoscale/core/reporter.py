import logging
import os
import signal
import threading
import time
from typing import List, Optional

from judoscale.core.adapter_api_client import api_client
from judoscale.core.config import config
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import MetricsCollector

logger = logging.getLogger(__name__)


class Reporter:
    """
    A reporter that collects metrics from all registered collectors and reports
    them to the Judoscale API.
    """

    def __init__(self):
        self._thread = None
        self._running = False
        self._stopevent = threading.Event()
        self.collectors: List[MetricsCollector] = []

    def add_collector(self, collector: MetricsCollector):
        """
        Add a collector to the reporter.
        """
        self.collectors.append(collector)

    def start(self):
        logger.info(f"Starting reporter for process {self.pid}")
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
    def pid(self):
        return os.getpid()

    def _run_loop(self):
        while self.is_running:
            self._report_metrics()
            time.sleep(config.report_interval_seconds)

            if self._stopevent.is_set():
                break

        logger.info(f"{self.pid} reports completed before exiting.")

    @property
    def all_metrics(self):
        """
        Return all metrics from all collectors.
        """
        metrics = []
        for collector in self.collectors:
            metrics.extend(collector.collect())
        return metrics

    def _report_metrics(self):
        api_client.post_report(self._build_report(self.all_metrics))

    def _build_report(self, metrics: List[Metric]):
        return {
            "dyno": config.dyno,
            "pid": self.pid,
            "config": config.for_report(),
            "metrics": [metric.as_tuple for metric in metrics],
        }


reporter = Reporter()
signal.signal(signal.SIGTERM, reporter.signal_handler)
