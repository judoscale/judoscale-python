import random
import time

from django_celery_sample.celery import app


@app.task
def add(x, y):
    time.sleep(random.randint(3, 5))
    return x + y
