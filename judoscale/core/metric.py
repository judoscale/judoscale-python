import re
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Tuple

from judoscale.core.logger import logger

nanoseconds = re.compile(r"^\d{19}$")
milliseconds = re.compile(r"^\d{13}$")
fractional_seconds = re.compile(r"^\d{10}.\d{3}$")


@dataclass
class Metric:
    timestamp: float  # Unix timestamp in fractional seconds
    value: int
    queue_name: Optional[str] = None
    measurement: str = "queue_time"

    @property
    def as_tuple(self) -> Tuple[int, int, str, Optional[str]]:
        """
        Return a tuple of the metric's timestamp, value, measurement and queue.
        """
        return (
            round(self.timestamp),
            self.value,
            self.measurement,
            self.queue_name,
        )

    @classmethod
    def new(cls, start_ms: int, **kwargs) -> "Metric":
        """
        Create a new Metric instance.

        start_ms:
            The start time the request or background job in milliseconds.
        """
        now = datetime.now(timezone.utc).timestamp()
        latency_ms = max(0, int(now * 1000) - start_ms)
        return cls(timestamp=now, value=latency_ms, **kwargs)

    @classmethod
    def for_web(cls, header_value: str) -> Optional["Metric"]:
        """
        Parse the X-Request-Start header value and return a Metric instance.

        There are several variants of this header. We handle these:
          - whole nanoseconds (Render)
          - whole milliseconds (Heroku)
          - fractional seconds (NGINX)
          - preceeding "t=" (NGINX)

        Calculate how long a request has been waiting to be handled, log and
        return a Metric instance.
        """

        request_start = re.sub(r"[^0-9.]", "", header_value)

        if re.match(nanoseconds, request_start):
            start_ms = int(float(request_start) / 1_000_000)
        elif re.match(milliseconds, request_start):
            start_ms = int(request_start)
        elif re.match(fractional_seconds, request_start):
            start_ms = int(float(request_start) * 1000)
        else:
            return None

        logger.debug(f"START X {start_ms}")
        metric = Metric.new(start_ms=start_ms)
        logger.debug(f"queue_time={metric.value}ms")
        return metric

    @classmethod
    def for_queue(cls, queue_name: str, oldest_job_ts: float) -> "Metric":
        """
        Calculate how long the oldest job in a queue has been waiting to be
        handled, log and return a Metric instance.

        queue_name:
            The name of the queue.

        oldest_job_ts:
            The Unix timestamp of the oldest job in the queue.
        """
        metric = Metric.new(start_ms=int(oldest_job_ts * 1000), queue_name=queue_name)
        logger.debug(f"queue_name={queue_name}, queue_time={metric.value}ms")
        return metric
