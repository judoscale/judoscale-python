import logging
import time
from celery import shared_task

logger = logging.getLogger(__name__)



@shared_task(bind=True)
def add(self, x, y):
    logger.info("Sleeping for 5 secs")
    time.sleep(5)
    amount = x + y
    logger.info("Done")
    return amount
