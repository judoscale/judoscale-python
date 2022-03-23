from dataclasses import dataclass
import datetime


@dataclass
class Metric:
    datetime: datetime
    value: float
    queue_name: str = None
    measurement: str = "queue_time"
