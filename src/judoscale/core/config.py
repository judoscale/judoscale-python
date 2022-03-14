import logging
import os

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        self.log_level = os.environ.get('LOG_LEVEL', 'INFO')
        self.dyno = os.environ.get('DYNO', None)
        self.report_interval_seconds = 10
        self.api_base_url = None
        self._prepare_logging()

    def merge(self, settings):
        for key in settings:
            setattr(self, key.lower(), settings[key])
        self._prepare_logging()

    def as_dict(self):
        return {
            'log_level': self.log_level,
            'report_interval_seconds': self.report_interval_seconds,
        }

    def _prepare_logging(self):
        log_level = logging.getLevelName(self.log_level.upper())
        logging.basicConfig(level=log_level, format='%(levelname)s - %(message)s', force=True)

config = Config()
