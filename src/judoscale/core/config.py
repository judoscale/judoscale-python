import logging
import os

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        self.log_level = os.environ.get('LOG_LEVEL', 'INFO')
        self.report_interval_seconds = 10
        self.api_base_url = None
        self._prepare_logging()

    def merge(self, settings):
        for key in settings:
            setattr(self, key.lower(), settings[key])
        self._prepare_logging()

    def _prepare_logging(self):
        log_level = logging.getLevelName(self.log_level.upper())
        logging.basicConfig(level=log_level, format='%(levelname)s - %(message)s', force=True)

config = Config()
