import os
import signal
import threading
import time
from platform import python_version
from typing import List

from judoscale.core.adapter import Adapter, AdapterInfo
from judoscale.core.adapter_api_client import api_client
from judoscale.core.config import config
from judoscale.core.logger import logger
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import Collector


class Reporter:
    """
    A reporter that collects metrics from all registered collectors and reports
    them to the Judoscale API.
    """

    def __init__(self):
        self._thread = None
        self._running = False
        self._stopevent = threading.Event()
        self.collectors: List[Collector] = []
        self.adapters: List[Adapter] = []

        self.adapters.append(
            Adapter(
                identifier="judoscale-python",
                adapter_info=AdapterInfo(platform_version=python_version()),
            )
        )

    def add_adapter(self, adapter: Adapter):
        """
        Add an adapter to the reporter.

        If the adapter has a metrics collector, it will be added to the list of
        collectors.
        """
        self.adapters.append(adapter)

        if adapter.metrics_collector:
            self.collectors.append(adapter.metrics_collector)

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
    def pid(self) -> int:
        return os.getpid()

    def _run_loop(self):
        while self.is_running:
            self._report_metrics()
            time.sleep(config.report_interval_seconds)

            if self._stopevent.is_set():
                break

        logger.info(f"{self.pid} reports completed before exiting.")

    @property
    def all_metrics(self) -> List[Metric]:
        """
        Return a list of all metrics collected by all collectors.
        """
        metrics = []
        for collector in self.collectors:
            metrics.extend(collector.collect())
        return metrics

    def _report_metrics(self) -> None:
        api_client.post_report(self._build_report(self.all_metrics))

    def _build_report(self, metrics: List[Metric]):
        return {
            "dyno": config.dyno,
            "pid": self.pid,
            "config": config.for_report(),
            "adapters": dict(adapter.as_tuple for adapter in self.adapters),
            "metrics": [metric.as_tuple for metric in metrics],
        }


reporter = Reporter()
signal.signal(signal.SIGTERM, reporter.signal_handler)
