import logging
import time, random

from django.conf import settings
from django.http import HttpResponse

logger = logging.getLogger(__name__)

def index(request):
    # Log message in level warning as this is Django's default logging level
    logger.warning("Hello, world")

    if request.GET.get("sleep"):
        time.sleep(random.randint(0,2))

    if url := settings.JUDOSCALE.get("API_BASE_URL"):
        return HttpResponse(
            "Judoscale Django Sample App. "
            f"<a target='_blank' href={url}>Metrics</a>"
        )
    else:
        return HttpResponse("Judoscale Django Sample App. No API URL provided.")
