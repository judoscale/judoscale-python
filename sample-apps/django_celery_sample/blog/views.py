import logging
import random

from blog.tasks import add
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

logger = logging.getLogger(__name__)


def publish_task(i=1):
    queue = "high" if random.random() > 0.5 else "low"
    logger.debug(f"Enqueuing a task on {queue=}")
    add.s(i, i).apply_async(queue=queue)


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
    catcher_url = settings.JUDOSCALE["API_BASE_URL"].replace("/inspect/", "/p/")
    return HttpResponse(
        "Judoscale Django Celery Sample App. "
        f"<a target='_blank' href={catcher_url}>Metrics</a>"
        "<form action='/task' method='POST'>"
        "<input type='submit' value='Add task'>"
        "</form>"
        "<form action='/batch_task' method='POST'>"
        "<input type='submit' value='Add 10 tasks'>"
        "</form>"
    )
