import logging

from django.apps import AppConfig
from django.conf import settings

from judoscale.core.config import config as judoconfig
from judoscale.core.reporter import reporter
from judoscale.django.redis import RedisHelper
from judoscale.rq import judoscale_rq

logger = logging.getLogger(__name__)


class JudoscaleRQConfig(AppConfig, RedisHelper):
    name = "judoscale.rq"
    label = "judoscale_rq"
    verbose_name = "Judoscale (RQ)"

    def ready(self):
        judoscale_config = getattr(settings, "JUDOSCALE", {})
        judoconfig.update(judoscale_config)

        if not judoconfig.is_enabled:
            logger.info("Not activated - No API URL provided")
            return

        judoscale_rq(self.redis_connection(judoscale_config.get("REDIS")))
        reporter.ensure_running()
