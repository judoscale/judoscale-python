import logging

from django.apps import AppConfig
from django.conf import settings
from judoscale.core.reporter import reporter
from judoscale.core.config import config

logger = logging.getLogger(__name__)


class JudoscaleDjangoConfig(AppConfig):
    name = "judoscale"
    verbose_name = "Judoscale (Django)"

    def ready(self):
        config.merge(getattr(settings, "JUDOSCALE", {}))

        if config.api_base_url is None:
            logger.info("Not activated - No API URL provided")
            return

        self.install_middleware()
        reporter.start()

    def install_middleware(self):
        if getattr(settings, "MIDDLEWARE", None) is None:
            logger.info("Unable to install middleware")
            return False

        logger.info("Installing middleware")

        judoscale_middleware = "judoscale.django.middleware.RequestQueueTimeMiddleware"

        # Prepend to MIDDLEWARE, handling both tuple and list form
        if isinstance(settings.MIDDLEWARE, tuple):
            if judoscale_middleware not in settings.MIDDLEWARE:
                settings.MIDDLEWARE = (judoscale_middleware,) + settings.MIDDLEWARE
        else:
            if judoscale_middleware not in settings.MIDDLEWARE:
                settings.MIDDLEWARE.insert(0, judoscale_middleware)
