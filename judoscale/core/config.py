import logging
import os
from collections import UserDict
from typing import Mapping

from judoscale.core.logger import logger

DEFAULTS = {"REPORT_INTERVAL_SECONDS": 10, "LOG_LEVEL": "WARN"}


class RuntimeContainer(str):
    @property
    def is_redundant_instance(self):
        instance_number = self.split(".")[-1]
        return instance_number.isdigit() and int(instance_number) > 1

    @property
    def is_release_instance(self):
        # NOTE: this is currently Heroku-specific. We may need to update this
        # for other platforms in the future and possibly move it to the Config
        # module.
        return self.lower().startswith("release")


class Config(UserDict):
    def __init__(
        self, runtime_container: RuntimeContainer, api_base_url: str, env: Mapping
    ):
        initialdata = dict(
            DEFAULTS,
            RUNTIME_CONTAINER=runtime_container,
            API_BASE_URL=api_base_url,
        )

        for key in {"RQ", "CELERY"}:
            if key in env:
                initialdata[key] = env[key]

        initialdata["LOG_LEVEL"] = env.get(
            "JUDOSCALE_LOG_LEVEL", env.get("LOG_LEVEL", initialdata["LOG_LEVEL"])
        )

        super().__init__(initialdata)
        self._prepare_logging()

    @classmethod
    def initialize(cls, env: Mapping = os.environ):
        if env.get("DYNO"):
            return cls.for_heroku(env)
        elif env.get("RENDER_INSTANCE_ID"):
            return cls.for_render(env)
        elif env.get("ECS_CONTAINER_METADATA_URI"):
            return cls.for_ecs(env)
        else:
            return cls(None, "", env)

    @classmethod
    def for_heroku(cls, env: Mapping):
        runtime_container = RuntimeContainer(env["DYNO"])
        api_base_url = env.get("JUDOSCALE_URL")
        return cls(runtime_container, api_base_url, env)

    @classmethod
    def for_render(cls, env: Mapping):
        service_id = env.get("RENDER_SERVICE_ID")
        instance = env.get("RENDER_INSTANCE_ID").replace(f"{service_id}-", "")
        runtime_container = RuntimeContainer(instance)
        api_base_url = f"https://adapter.judoscale.com/api/{service_id}"
        return cls(runtime_container, api_base_url, env)

    @classmethod
    def for_ecs(cls, env: Mapping):
        instance = env["ECS_CONTAINER_METADATA_URI"].split("/")[-1]
        runtime_container = RuntimeContainer(instance)
        api_base_url = env.get("JUDOSCALE_URL")
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
