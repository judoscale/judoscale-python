import logging
import random

from blog.tasks import add_high, add_low
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


def publish_task(i=1):
    if random.random() > 0.5:
        logger.debug("Enqueuing a task on queue='high'")
        add_high.send(i, i)
    else:
        logger.debug("Enqueuing a task on queue='low'")
        add_low.send(i, i)


@csrf_exempt
def one_task(request):
    publish_task()
    return redirect("/")


@csrf_exempt
def many_tasks(request):
    for i in range(10):
        publish_task(i)
    return redirect("/")


def index(request):
    logger.warning("Hello, world")
    if url := settings.JUDOSCALE.get("API_BASE_URL"):
        return HttpResponse(
            "Judoscale Django Dramatiq Sample App. "
            f"<a target='_blank' href={url}>Metrics</a>"
            "<form action='/task' method='POST'>"
            "<input type='submit' value='Add task'>"
            "</form>"
            "<form action='/batch_task' method='POST'>"
            "<input type='submit' value='Add 10 tasks'>"
            "</form>"
        )
    else:
        return HttpResponse(
            "Judoscale Django Dramatiq Sample App. No API URL provided."
        )
