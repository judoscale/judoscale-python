import random
import time

import app.settings as settings
from celery import Celery

from judoscale.celery import judoscale_celery

celery = Celery("CelerySampleApp", broker="redis://localhost:6379/0")

judoscale_celery(celery, extra_config=settings.JUDOSCALE)


@celery.task
def add(x, y):
    time.sleep(random.randint(3, 5))
    return x + y
