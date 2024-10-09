import os
import signal
import sys
import threading
import time
from platform import python_version
from typing import List

import requests

from judoscale.core.adapter import Adapter, AdapterInfo
from judoscale.core.config import Config, config
from judoscale.core.logger import logger
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import Collector


class Reporter:
    """
    A reporter that collects metrics from all registered collectors and reports
    them to the Judoscale API.
    """

    def __init__(self, config: Config):
        self.config = config
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
        if not self.config.is_enabled:
            logger.info("Reporter not started: API_BASE_URL not set")
            return

        if self.config["RUNTIME_CONTAINER"] is None:
            logger.info("Reporter not started: unknown runtime container")
            return

        if self.config["RUNTIME_CONTAINER"].is_release_instance:
            logger.info("Reporter not started: in a build process")
            return

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
            # NOTE: we used to report metrics immediately after the process
            # started, but this caused issues with Celery and Celery Beat
            # when TRACK_BUSY_JOBS was enabled.
            # Instead, we now wait for the first interval to pass before
            # reporting metrics.
            time.sleep(self.config["REPORT_INTERVAL_SECONDS"])
            self._report_metrics()

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
        report = self._build_report(self.all_metrics)
        url = f"{self.config['API_BASE_URL']}/v3/reports"
        try:
            metrics_length = len(report["metrics"])
            pid = report["pid"]
            logger.debug(
                f"Posting {metrics_length} metrics from {pid} "
                f"to Judoscale adapter API {url}"
            )
            response = requests.post(url, timeout=5, json=report)
            response.raise_for_status()
        except requests.RequestException as e:
            logger.warning("Adapter API request failed - {}".format(e))

    def _build_report(self, metrics: List[Metric]):
        return {
            "container": str(self.config["RUNTIME_CONTAINER"]),
            "pid": self.pid,
            "config": self.config.for_report,
            "adapters": dict(adapter.as_tuple for adapter in self.adapters),
            "metrics": [metric.as_tuple for metric in metrics],
        }


reporter = Reporter(config=config)

previous_handler = signal.getsignal(signal.SIGTERM)


def graceful_shutdown(signum, frame):
    reporter.signal_handler(signum, frame)
    # If there was a previous handler and it's not SIG_DFL or SIG_IGN, call it
    if callable(previous_handler) and previous_handler not in (
        signal.SIG_DFL,
        signal.SIG_IGN,
    ):
        previous_handler(signum, frame)
    else:
        # If no previous handler, use default behavior (exit the process)
        sys.exit(0)


signal.signal(signal.SIGTERM, graceful_shutdown)
