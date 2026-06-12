import logging
import os
from collections import UserDict
from typing import Mapping

from judoscale.core.logger import logger
from judoscale.core.platform import Platform

DEFAULTS = {"REPORT_INTERVAL_SECONDS": 10, "LOG_LEVEL": "WARN"}


class Config(UserDict):
    def __init__(self, platform: Platform, env: Mapping):
        initialdata = dict(
            DEFAULTS,
            PLATFORM=platform,
            API_BASE_URL=env.get("JUDOSCALE_URL"),
        )

        for key in {"RQ", "CELERY"}:
            if key in env:
                initialdata[key] = env[key]

        initialdata["LOG_LEVEL"] = env.get(
            "JUDOSCALE_LOG_LEVEL", env.get("LOG_LEVEL", initialdata["LOG_LEVEL"])
        )

        # Legacy Render services not using JUDOSCALE_URL derive the API url from
        # the platform.
        if not initialdata["API_BASE_URL"]:
            initialdata["API_BASE_URL"] = platform.default_api_base_url

        super().__init__(initialdata)
        self._prepare_logging()

    @classmethod
    def initialize(cls, env: Mapping = os.environ):
        return cls(Platform.detect(env), env)

    @property
    def is_enabled(self) -> bool:
        return bool(self["API_BASE_URL"])

    def update(self, new_config: Mapping):
        for k, v in new_config.items():
            k = k.upper()
            if k in self and isinstance(self[k], dict) and isinstance(v, dict):
                self[k].update(v)
            else:
                self[k] = v
        self._prepare_logging()

    def merge(self, new_config: Mapping):
        logger.warning("Config.merge() is deprecated. Use Config.update() instead.")
        self.update(new_config)

    @property
    def for_report(self):
        # Only include the config options we want to include in the report
        return {
            "log_level": self["LOG_LEVEL"],
            "report_interval_seconds": self["REPORT_INTERVAL_SECONDS"],
        }

    def _prepare_logging(self):
        log_level = logging.getLevelName(self["LOG_LEVEL"].upper())
        logger.setLevel(log_level)

        if not logger.handlers:
            stdout_handler = logging.StreamHandler()
            fmt = "%(levelname)s - [%(name)s] %(message)s"
            stdout_handler.setFormatter(logging.Formatter(fmt))
            logger.addHandler(stdout_handler)


config = Config.initialize()
