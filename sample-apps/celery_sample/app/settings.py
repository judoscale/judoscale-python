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
        "API_BASE_URL": "https://requestinspector.com/inspect/judoscale-celery",
        "LOG_LEVEL": "DEBUG",
        "REPORT_INTERVAL_SECONDS": 15,
    }
