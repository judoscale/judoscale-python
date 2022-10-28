import os
from celery import Celery
from datetime import datetime as dt

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "celery_sample.settings")

# Create a new instance of Celery
app = Celery("celery_sample")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()


if __name__ == "__main__":
    app.start()
