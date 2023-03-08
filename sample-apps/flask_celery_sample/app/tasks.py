import random
import time

from app.settings import BaseConfig
from celery import Celery

from judoscale.celery import judoscale_celery

celery = Celery("CelerySampleApp", broker="redis://localhost:6379/0")

judoscale_celery(celery, extra_config=BaseConfig.JUDOSCALE)


@celery.task
def add(x, y):
    time.sleep(random.randint(3, 5))
    return x + y
