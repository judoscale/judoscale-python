import logging
import os

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        self.log_level = os.environ.get('LOG_LEVEL', 'INFO')
        log_level = logging.getLevelName(self.log_level.upper())
        logging.basicConfig(level=log_level, format='%(levelname)s - %(message)s')

config = Config()
