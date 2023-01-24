import logging

from django.conf import settings
from django.http import HttpResponse

logger = logging.getLogger(__name__)


def index(request):
    # Log message in level warning as this is Django's default logging level
    logger.warning("Hello, world")
    return HttpResponse(
        "Judoscale Django Sample App. "
        f"<a target='_blank' href={settings.JUDOSCALE['API_BASE_URL']}>Metrics</a>"
    )
