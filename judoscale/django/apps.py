import logging

from django.apps import AppConfig
from django.conf import settings

from judoscale.core.config import config as judoconfig
from judoscale.core.reporter import reporter

logger = logging.getLogger(__name__)


class JudoscaleDjangoConfig(AppConfig):
    name = "judoscale"
    verbose_name = "Judoscale (Django)"

    def ready(self):
        judoconfig.merge(getattr(settings, "JUDOSCALE", {}))

        if judoconfig.api_base_url is None:
            logger.info("Not activated - No API URL provided")
            return

        self.install_middleware()
        reporter.ensure_running()

    def install_middleware(self):
        if getattr(settings, "MIDDLEWARE", None) is None:
            logger.info("Unable to install middleware")
            return False

        judoscale_middleware = "judoscale.django.middleware.RequestQueueTimeMiddleware"

        # Prepend to MIDDLEWARE, handling both tuple and list form
        if judoscale_middleware not in settings.MIDDLEWARE:
            logger.info("Installing middleware")
            if isinstance(settings.MIDDLEWARE, tuple):
                settings.MIDDLEWARE = (judoscale_middleware,) + settings.MIDDLEWARE
            else:  # it is a list
                settings.MIDDLEWARE.insert(0, judoscale_middleware)
