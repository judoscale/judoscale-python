from datetime import datetime
import re

class RequestQueueTimeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_start_header = request.META.get("HTTP_X_REQUEST_START", "")

        # Remove non-digits. This removes the "t=" prefix added by some web servers (NGINX).
        # NGINX also reports this time as fractional seconds with millisecond resolution,
        # so removing the decimal gives us integer milliseconds (same as Heroku).
        request_start_header = re.sub(r"\D", '', request_start_header)

        request_start_timestamp_ms = int(request_start_header)
        current_timestamp_ms = datetime.now().timestamp() * 1000

        queue_time_ms = current_timestamp_ms - request_start_timestamp_ms
        print('TODO: store queue_time ({}ms)'.format(round(queue_time_ms)))

        return self.get_response(request)
