import time

# from celery_sample.celery import app
from celery import shared_task


@shared_task(bind=True)
# @app.task(bind=True)
def add(self, x, y):
    print("SLEEPING for 60''")
    time.sleep(60)
    amount = x + y
    print("Done")
    return amount
