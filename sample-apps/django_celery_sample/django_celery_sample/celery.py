from celery import Celery
from django.conf import settings

from judoscale.celery import judoscale_celery

app = Celery("DjangoCelerySampleApp")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

judoscale_celery(app, extra_config=settings.JUDOSCALE)
