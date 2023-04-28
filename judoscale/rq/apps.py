import logging
import os

from django.apps import AppConfig
from django.conf import settings
from redis import Redis

from judoscale.core.config import config as judoconfig
from judoscale.core.reporter import reporter
from judoscale.rq import judoscale_rq

logger = logging.getLogger(__name__)


class JudoscaleRQConfig(AppConfig):
    name = "judoscale.rq"
    label = "judoscale_rq"
    verbose_name = "Judoscale (RQ)"

    def ready(self):
        judoconfig.update(getattr(settings, "JUDOSCALE", {}))

        if not judoconfig.is_enabled:
            logger.info("Not activated - No API URL provided")
            return

        judoscale_rq(self.redis_connection)
        reporter.ensure_running()

    @property
    def redis_connection(self):
        """
        Return a Redis connection from an RQ queue configuration
        """
        if redis_config := settings.JUDOSCALE.get("REDIS"):
            config = {k.lower(): v for k, v in redis_config.items()}
            if redis_url := config.get("url"):
                return Redis.from_url(redis_url)
            else:
                return Redis(**config)
        elif redis_url := os.getenv("REDIS_URL"):
            return Redis.from_url(redis_url)
        else:
            raise RuntimeError(
                "Missing Redis connection configuration. Please set either "
                "settings.JUDOSCALE['REDIS'] or REDIS_URL environment variable."
            )
