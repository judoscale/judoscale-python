import logging
import random
import time

import django_rq
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


def add(x, y):
    time.sleep(random.randint(3, 5))
    return x + y


def publish_task(i=1):
    queue = django_rq.get_queue("high" if random.random() > 0.5 else "low")
    logger.debug(f"Enqueuing a task on {queue=}")
    queue.enqueue(add, i, i)


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
    # Log message in level warning as this is Django's default logging level
    logger.warning("Hello, world")
    if url := settings.JUDOSCALE.get("API_BASE_URL"):
        return HttpResponse(
            "Judoscale Django RQ Sample App. "
            f"<a target='_blank' href={url}>Metrics</a>"
            "<form action='/task' method='POST'>"
            "<input type='submit' value='Add task'>"
            "</form>"
            "<form action='/batch_task' method='POST'>"
            "<input type='submit' value='Add 10 tasks'>"
            "</form>"
        )
    else:
        return HttpResponse("Judoscale Django RQ Sample App. No API URL provided.")
