import os
import logging

logger = logging.getLogger('judoscale')
log_level = os.environ.get("LOG_LEVEL", "DEBUG")
logger.setLevel(log_level.upper())

stdout_handler = logging.StreamHandler()
stdout_handler.setLevel(logging.DEBUG)
fmt = "%(levelname)s - [Judoscale] %(message)s"
stdout_handler.setFormatter(logging.Formatter(fmt))
logger.addHandler(stdout_handler)
