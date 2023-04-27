import logging

from django.conf import settings
from django.http import HttpResponse

logger = logging.getLogger(__name__)


def index(request):
    # Log message in level warning as this is Django's default logging level
    logger.warning("Hello, world")
    if url := settings.JUDOSCALE.get("API_BASE_URL"):
        catcher_url = url.replace("/inspect/", "/p/")
        return HttpResponse(
            "Judoscale Django Sample App. "
            f"<a target='_blank' href={catcher_url}>Metrics</a>"
        )
    else:
        return HttpResponse("Judoscale Django Sample App. No API URL provided.")
