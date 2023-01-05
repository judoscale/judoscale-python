import datetime
import logging
import re
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Metric:
    datetime: datetime
    value: float
    queue_name: str = None
    measurement: str = "queue_time"


class RequestMetrics:
    def __init__(self, request_header):
        self.request_header = request_header

    def get_queue_time_metric_from_header(self):
        """
        Remove non-digits:
            This removes the "t=" prefix added by some web servers (NGINX).
        Remove decimal:
            NGINX also reports this time as fractional seconds with millisecond
            resolution, so removing the decimal gives us integer milliseconds
            (same as Heroku).
        Then, we calculate the timelapse between request start and finish,
            log and send it to judoscale reporter.
        """
        request_header = re.sub(r"\D", "", self.request_header)

        if len(request_header) > 0:
            logger.debug(f"START X {request_header}")
            now = datetime.datetime.now()
            request_start_timestamp_ms = int(request_header)
            current_timestamp_ms = now.timestamp() * 1000
            queue_time_ms = current_timestamp_ms - request_start_timestamp_ms
            metric = Metric(measurement="queue_time", datetime=now, value=queue_time_ms)
            logger.debug("queue_time={}ms".format(round(queue_time_ms, 2)))
            return metric

        else:
            return None
