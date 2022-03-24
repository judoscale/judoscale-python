import re
import logging
from datetime import datetime
from judoscale.core.metrics_store import metrics_store
from judoscale.core.metric import Metric

logger = logging.getLogger(__name__)


class RequestQueueTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_start_header = request.META.get("HTTP_X_REQUEST_START", "")

        # Remove non-digits. This removes the "t=" prefix added by some web servers (NGINX).
        # NGINX also reports this time as fractional seconds with millisecond resolution,
        # so removing the decimal gives us integer milliseconds (same as Heroku).
        request_start_header = re.sub(r"\D", "", request_start_header)

        if len(request_start_header) > 0:
            now = datetime.now()
            request_start_timestamp_ms = int(request_start_header)
            current_timestamp_ms = now.timestamp() * 1000
            queue_time_ms = current_timestamp_ms - request_start_timestamp_ms
            metric = Metric(measurement="queue_time", datetime=now, value=queue_time_ms)

            metrics_store.add(metric)
            logger.debug("queue_time={}ms".format(round(queue_time_ms, 2)))

        return self.get_response(request)
