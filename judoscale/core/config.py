import logging
import os
from typing import Mapping

from judoscale.core.logger import logger


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


class Config:
    def __init__(
        self, runtime_container: RuntimeContainer, api_base_url: str, log_level: str
    ):
        self.runtime_container = runtime_container
        self.log_level = log_level
        self.report_interval_seconds = 10
        self.api_base_url = api_base_url
        self._prepare_logging()

    @classmethod
    def initialise(cls, env: Mapping = os.environ):
        if env.get("DYNO"):
            return cls.for_heroku(env)
        elif env.get("RENDER_INSTANCE_ID"):
            return cls.for_render(env)
        else:
            return cls(None, "", "INFO")

    @classmethod
    def for_heroku(cls, env: Mapping):
        service_name, instance = env.get("DYNO").split(".")
        service_type = "web" if service_name == "web" else "other"

        runtime_container = RuntimeContainer(service_name, instance, service_type)
        api_base_url = env.get("JUDOSCALE_URL")
        log_level = env.get("LOG_LEVEL", "INFO").upper()
        return cls(runtime_container, api_base_url, log_level)

    @classmethod
    def for_render(cls, env: Mapping):
        service_id = env.get("RENDER_SERVICE_ID")
        instance = env.get("RENDER_INSTANCE_ID").replace(f"{service_id}-", "")
        service_type = env.get("RENDER_SERVICE_TYPE")

        runtime_container = RuntimeContainer(service_id, instance, service_type)
        api_base_url = f"https://adapter.judoscale.com/api/{service_id}"
        log_level = env.get("LOG_LEVEL", "INFO").upper()
        return cls(runtime_container, api_base_url, log_level)

    def merge(self, settings: Mapping):
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


config = Config.initialise()
