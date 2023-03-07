import logging

from celery import Celery
from django.apps import AppConfig
from django.conf import settings

from judoscale.celery import judoscale_celery
from judoscale.core.config import config as judoconfig

logger = logging.getLogger(__name__)


class JudoscaleCeleryConfig(AppConfig):
    name = "judoscale.celery"
    label = "judoscale_celery"
    verbose_name = "Judoscale (Celery)"

    def ready(self):
        judoconfig.merge(getattr(settings, "JUDOSCALE", {}))

        if judoconfig.api_base_url is None:
            logger.info("Not activated - No API URL provided")
            return

        celery = Celery(self.name, broker=settings.CELERY_BROKER_URL)
        judoscale_celery(celery)
