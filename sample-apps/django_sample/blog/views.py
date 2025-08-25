import logging
import time, random

from django.conf import settings
from django.http import HttpResponse

from judoscale.core.utilization_tracker import utilization_tracker

logger = logging.getLogger(__name__)

def index(request):
    # Log message in level warning as this is Django's default logging level
    logger.warning("Hello, world")

    if sleep_for := request.GET.get("sleep"):
        try:
            sleep_for = float(sleep_for)
        except:
            sleep_for = random.randint(0, 2)
        time.sleep(sleep_for)

    if url := settings.JUDOSCALE.get("API_BASE_URL"):
        return HttpResponse(
            "Judoscale Django Sample App. "
            f"<a target='_blank' href={url}>Metrics</a>"
        )
    else:
        return HttpResponse("Judoscale Django Sample App. No API URL provided.")

def test_utilization_tracker(request):
    # Run utilization tracker in the foreground to execute the tracking mid-request.
    utilization_tracker._track_current_state()

    return HttpResponse(f"utilization_tracker={utilization_tracker.active_requests}")
