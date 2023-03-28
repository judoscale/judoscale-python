import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Tuple

from judoscale.core.logger import logger

# Adapted from https://github.com/scoutapp/scout_apm_python/blob/86d14920a59a7a3b5dfffe680586646ee29bdd7a/src/scout_apm/core/web_requests.py#L139-L162 # noqa: E501
# Cutoff epoch is used for determining ambiguous timestamp boundaries
CUTOFF_EPOCH_MS = time.mktime((2000, 1, 1, 0, 0, 0, 0, 0, 0)) * 1000
CUTOFF_EPOCH_US = CUTOFF_EPOCH_MS * 1000
CUTOFF_EPOCH_NS = CUTOFF_EPOCH_US * 1000


def convert_ambiguous_timestamp_to_ms(timestamp: float) -> int:
    """
    Convert an ambiguous float timestamp that could be in nanoseconds,
    microseconds, milliseconds, or seconds to nanoseconds.
    Return None for values in the more than 10 years ago.
    """
    if timestamp > CUTOFF_EPOCH_NS:
        return int(timestamp / 1_000_000.0)
    elif timestamp > CUTOFF_EPOCH_US:
        return int(timestamp / 1_000.0)
    elif timestamp > CUTOFF_EPOCH_MS:
        return int(timestamp)
    else:
        return int(timestamp * 1_000.0)


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
          - nanoseconds (Render)
          - microseconds (???)
          - milliseconds (Heroku)
          - fractional seconds (NGINX)
          - preceeding "t=" (NGINX)

        Calculate how long a request has been waiting to be handled, log and
        return a Metric instance.
        """

        if header_value.startswith("t="):
            header_value = header_value[2:]

        if not header_value or not header_value[0].isdigit():
            return None

        try:
            ambiguous_timestamp = float(header_value)
        except ValueError:
            return None

        start_ms = convert_ambiguous_timestamp_to_ms(ambiguous_timestamp)
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

    @classmethod
    def for_busy_queue(cls, queue_name: str, busy_jobs: int) -> "Metric":
        """
        Log and return a Metric instance for the number of jobs being processed
        for a given queue.

        queue_name:
            The name of the queue.

        busy_jobs:
            The number of jobs being processed for the given queue.
        """
        metric = Metric(
            measurement="busy",
            queue_name=queue_name,
            value=busy_jobs,
            timestamp=time.time(),
        )
        logger.debug(f"queue_name={queue_name}, busy_jobs={metric.value}")
        return metric
