import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseConfig:
    BASE_DIR = Path(__file__).parent.resolve()
    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True

    SECRET_KEY = os.getenv("SECRET_KEY", "")

    JUDOSCALE = {
        "API_BASE_URL": "https://judoscale-python.requestcatcher.com",
        "LOG_LEVEL": "DEBUG",
        # "REPORT_INTERVAL_SECONDS": 5,
        # Same as default settings in Config.DEFAULTS
        "RQ": {
            "ENABLED": True,
            "MAX_QUEUES": 20,
            "QUEUES": [],
        },
    }
