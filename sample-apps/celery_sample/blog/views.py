import logging

from django.http import HttpResponse
from blog.tasks import add

logger = logging.getLogger(__name__)


def index(request):
    """ Emmit log message in level warning as this is Django's default level
    to output messages in the console stream
    """

    logger.warning("Hello, world")
    add.delay(1, 3)

    return HttpResponse("Judoscale Sample App")
