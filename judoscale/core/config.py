import logging
import os

from judoscale.core.logger import logger


class Config:
    def __init__(self):
        self.log_level = os.environ.get("LOG_LEVEL", "INFO")
        self.dyno = os.environ.get("DYNO", "none.0")
        self.dyno_name, self.dyno_num = self.dyno.split(".")
        self.dyno_num = int(self.dyno_num)
        self.report_interval_seconds = 10
        self.api_base_url = os.environ.get("JUDOSCALE_URL")
        self._prepare_logging()

    def merge(self, settings: dict):
        for key, value in settings.items():
            setattr(self, key.lower(), value)
        self._prepare_logging()

    def for_report(self):
        # Only include the config options we want to include in the report
        return {
            "log_level": self.log_level,
            "report_interval_seconds": self.report_interval_seconds,
        }

    def _prepare_logging(self):
        log_level = logging.getLevelName(self.log_level.upper())
        logger.setLevel(log_level)

        if not logger.handlers:
            stdout_handler = logging.StreamHandler()
            fmt = "%(levelname)s - [%(name)s] %(message)s"
            stdout_handler.setFormatter(logging.Formatter(fmt))
            logger.addHandler(stdout_handler)

        logger.propagate = False


config = Config()
