from judoscale.core.config import config
import threading
import time
import logging

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')

def loop():
    logging.debug("start loop")
    while True:
        logging.debug("TODO: report")
        time.sleep(2)

class Reporter:
    _thread = None

    @classmethod
    def start(cls):
        logging.debug("starting reporter")
        cls._thread = threading.Thread(target=loop, daemon=True)
        cls._thread.start()
