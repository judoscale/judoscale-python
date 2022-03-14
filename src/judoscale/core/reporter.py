import threading
import time
import logging
from judoscale.core.config import config
from judoscale.core.metrics_store import metrics_store
from judoscale.core.adapter_api_client import api_client
from judoscale.core.report import Report

logger = logging.getLogger(__name__)

class Reporter:
    _thread = None

    @classmethod
    def start(cls):
        logger.info("[Judoscale] Starting reporter")
        cls._thread = threading.Thread(target=cls._run_loop, daemon=True)
        cls._thread.start()

    @classmethod
    def _run_loop(cls):
        while True:
            cls._report_metrics()
            time.sleep(config.report_interval_seconds)

    @classmethod
    def _report_metrics(cls):
        metrics = metrics_store.flush()
        report = Report(metrics, config)
        api_client.post_report(report)
