import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class JudoscaleMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_start_header = request.META.get("HTTP_X_REQUEST_START", "")

        # Remove non-digits. This removes the "t=" prefix added by some web servers (NGINX).
        # NGINX also reports this time as fractional seconds with millisecond resolution,
        # so removing the decimal gives us integer milliseconds (same as Heroku).
        request_start_header = re.sub(r"\D", '', request_start_header)
        logger.debug('request_start_header={}'.format(request_start_header))

        request_start_timestamp_ms = int(request_start_header)
        current_timestamp_ms = datetime.now().timestamp() * 1000
        logger.debug('request_start_timestamp_ms={}'.format(request_start_timestamp_ms))
        logger.debug('current_timestamp_ms={}'.format(current_timestamp_ms))

        queue_time_ms = current_timestamp_ms - request_start_timestamp_ms
        logger.debug('queue_time_ms={}'.format(queue_time_ms))

        return self.get_response(request)
