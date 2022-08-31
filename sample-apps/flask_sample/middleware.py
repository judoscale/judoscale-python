import re
import logging
from datetime import datetime

from werkzeug.wrappers import Request  # , Response, ResponseStream

from judoscale.core.metrics_store import metrics_store
from judoscale.core.metric import Metric
from judoscale.core.reporter import reporter

logger = logging.getLogger(__name__)


class RequestQueueTimeMiddleware:
    """ WSGI middleware for query metrics report"""

    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        """ Request META is fist cleared with regular expression substitutions.
        Remove non-digits:
            This removes the "t=" prefix added by some web servers (NGINX).
        Remove decimal:
            NGINX also reports this time as fractional seconds with millisecond
            resolution, so removing the decimal gives us integer milliseconds
            (same as Heroku).
        Then, we calculate the timelapse between request start and finish,
            log and send it to judoscale reporter.
        """

        request = Request(environ)
        logger.debug(request)

        request_start_header = request.get("HTTP_X_REQUEST_START", "")
        request_start_header = re.sub(r"\D", "", request_start_header)

        if len(request_start_header) > 0:
            now = datetime.now()
            request_start_timestamp_ms = int(request_start_header)
            current_timestamp_ms = now.timestamp() * 1000
            queue_time_ms = current_timestamp_ms - request_start_timestamp_ms
            metric = Metric(measurement="queue_time",
                            datetime=now,
                            value=queue_time_ms)

            metrics_store.add(metric)
            logger.debug("queue_time={}ms".format(round(queue_time_ms, 2)))
            reporter.ensure_running()

        return self.app(environ, start_response)
