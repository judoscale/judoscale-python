# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent

import logging
import os
from pathlib import Path
# from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class BaseConfig(object):
    # load env variables from dotenv
    BASE_DIR = Path(__file__).parent.resolve()
#    ENV = os.getenv("FLASK_ENV", "").lower()
#    env_filepath = Path(BASE_DIR).joinpath(".{}.env".format(ENV))
    # SECURITY WARNING: don't run with debug turned on in production!
    DEBUG = True

#    if Path(env_filepath).is_file():
#        # load environment variables from dotenv
#        load_dotenv(env_filepath, verbose=True)
#    else:
#        logger.warning(
#            "WARNING: env file %s does not exist!", env_filepath
#        )

    SECRET_KEY = os.getenv("SECRET_KEY", "")
    API_BASE_URL = "https://judoscale-python.requestcatcher.com",

    JUDOSCALE = {
        # This sample app is intended to be run locally,
        # so Judoscale API requests are sent to a mock endpoint.
        "API_BASE_URL": "https://judoscale-python.requestcatcher.com",
        "LOG_LEVEL": "DEBUG",
        "REPORT_INTERVAL_SECONDS": 2,
    }
