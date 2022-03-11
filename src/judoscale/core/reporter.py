import threading
import time
import logging
from judoscale.core.config import config
from judoscale.core.metrics_store import metrics_store

logger = logging.getLogger(__name__)

class Reporter:
    _thread = None

    @classmethod
    def start(cls):
        logger.info("[Judoscale] Starting reporter")
        cls._thread = threading.Thread(target=cls.loop, daemon=True)
        cls._thread.start()

    @classmethod
    def loop(cls):
        while True:
            metrics = metrics_store.flush()
            logger.debug("TODO: report {} metrics".format(len(metrics)))
            time.sleep(2)
