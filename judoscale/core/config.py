import logging
import os
from collections import UserDict
from typing import Mapping

from judoscale.core.logger import logger

DEFAULTS = {"REPORT_INTERVAL_SECONDS": 10, "LOG_LEVEL": "WARN"}


class RuntimeContainer:
    def __init__(self, service_name, instance, service_type):
        self.service_name = service_name
        self.instance = instance
        self.service_type = service_type

    @property
    def is_web_instance(self):
        return self.service_name == "web" or self.service_type == "web"

    @property
    def is_redundant_instance(self):
        return self.instance.isdigit() and self.instance != "1"

    def __str__(self):
        return f"{self.service_name}.{self.instance}"


class Config(UserDict):
    def __init__(
        self, runtime_container: RuntimeContainer, api_base_url: str, env: Mapping
    ):
        initialdata = dict(
            DEFAULTS,
            RUNTIME_CONTAINER=runtime_container,
            API_BASE_URL=api_base_url,
        )

        for key in {"LOG_LEVEL", "RQ", "CELERY"}:
            if key in env:
                initialdata[key] = env[key]

        super().__init__(initialdata)
        self._prepare_logging()

    @classmethod
    def initialize(cls, env: Mapping = os.environ):
        if env.get("DYNO"):
            return cls.for_heroku(env)
        elif env.get("RENDER_INSTANCE_ID"):
            return cls.for_render(env)
        else:
            return cls(None, "", env)

    @classmethod
    def for_heroku(cls, env: Mapping):
        service_name, instance = env.get("DYNO").split(".")
        service_type = "web" if service_name == "web" else "other"

        runtime_container = RuntimeContainer(service_name, instance, service_type)
        api_base_url = env.get("JUDOSCALE_URL")
        return cls(runtime_container, api_base_url, env)

    @classmethod
    def for_render(cls, env: Mapping):
        service_id = env.get("RENDER_SERVICE_ID")
        instance = env.get("RENDER_INSTANCE_ID").replace(f"{service_id}-", "")
        service_type = env.get("RENDER_SERVICE_TYPE")

        runtime_container = RuntimeContainer(service_id, instance, service_type)
        api_base_url = f"https://adapter.judoscale.com/api/{service_id}"
        return cls(runtime_container, api_base_url, env)

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
