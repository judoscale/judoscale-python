from dataclasses import dataclass

@dataclass
class Metric:
  value: float
  queue_name: str = None
  measurement: str = "queue_time"
