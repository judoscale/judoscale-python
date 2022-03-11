import django
import logging
from django.apps import AppConfig

logger = logging.getLogger(__name__)

class JudoscaleDjangoConfig(AppConfig):
  name = "judoscale"
  verbose_name = "Judoscale (Django)"

  def ready(self):
    logger.debug("JudoscaleDjangoConfig ready")
