from django.apps import AppConfig
from judoscale.core.reporter import Reporter

class JudoscaleDjangoConfig(AppConfig):
    name = "judoscale"
    verbose_name = "Judoscale (Django)"

    def ready(self):
        self.install_middleware()
        Reporter.start()

    def install_middleware(self):
        print("Installing Judoscale middleware")

        from django.conf import settings

        if getattr(settings, "MIDDLEWARE", None) is None:
            return False

        judoscale_middleware = "judoscale.django.middleware.RequestQueueTimeMiddleware"

        # Prepend to MIDDLEWARE, handling both tuple and list form
        if isinstance(settings.MIDDLEWARE, tuple):
            if judoscale_middleware not in settings.MIDDLEWARE:
                settings.MIDDLEWARE = (judoscale_middleware,) + settings.MIDDLEWARE
        else:
            if judoscale_middleware not in settings.MIDDLEWARE:
                settings.MIDDLEWARE.insert(0, judoscale_middleware)
