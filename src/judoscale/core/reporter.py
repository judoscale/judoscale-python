from judoscale.core.config import config
import threading
import time
import logging

logger = logging.getLogger(__name__)

def loop():
    logger.debug("start loop")
    while True:
        logger.debug("TODO: report")
        time.sleep(2)

class Reporter:
    _thread = None

    @classmethod
    def start(cls):
        logger.debug("starting reporter")
        cls._thread = threading.Thread(target=loop, daemon=True)
        cls._thread.start()
