import logging
import os

logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        self.log_level = os.environ.get("LOG_LEVEL", "INFO")
        self.dyno = os.environ.get("DYNO", None)
        self.report_interval_seconds = 10
        self.api_base_url = os.environ.get("JUDOSCALE_URL", None)
        self._prepare_logging()

    def merge(self, settings):
        for key in settings:
            setattr(self, key.lower(), settings[key])
        self._prepare_logging()

    def for_report(self):
        # Only include the config options we want to include in the report
        return {
            "log_level": self.log_level,
            "report_interval_seconds": self.report_interval_seconds,
        }

    def _prepare_logging(self):
        log_level = logging.getLevelName(self.log_level.upper())
        logging.basicConfig(
            level=log_level,
            format="%(levelname)s - [Judoscale] %(message)s",
            force=True,
        )


config = Config()
