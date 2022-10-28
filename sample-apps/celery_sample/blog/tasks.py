import time

# from celery_sample.celery import app as celery_app
# from celery_sample.celery import CeleryEventsHandler
from celery import shared_task


@shared_task(bind=True)
#@celery_app.task(bind=True)
def add(self, x, y):
    print("SLEEPING for 5''")
    time.sleep(5)
    amount = x + y
    print("Done")
    return amount


# events_handler = CeleryEventsHandler(celery_app)
# events_handler.start_listening()
