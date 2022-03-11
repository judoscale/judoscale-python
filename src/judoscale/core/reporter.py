import threading
import time
import logging
from judoscale.core.config import config
from judoscale.core.metrics_store import metrics_store

logger = logging.getLogger(__name__)

def loop():
    while True:
        metrics = metrics_store.flush()
        logger.debug("TODO: report {} metrics".format(len(metrics)))
        time.sleep(2)

class Reporter:
    _thread = None

    @classmethod
    def start(cls):
        logger.debug("Starting Judoscale reporter")
        cls._thread = threading.Thread(target=loop, daemon=True)
        cls._thread.start()
