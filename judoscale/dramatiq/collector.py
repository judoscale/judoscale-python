import json
import time
from typing import List, Optional

from dramatiq.brokers.redis import RedisBroker

from judoscale.core.config import Config
from judoscale.core.logger import logger
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import JobMetricsCollector

DEFAULTS = {
    "ENABLED": True,
    "MAX_QUEUES": 20,
    "QUEUES": [],
}


class DramatiqMetricsCollector(JobMetricsCollector):
    def __init__(self, config: Config, broker: RedisBroker):
        super().__init__(config=config)

        self.config["DRAMATIQ"] = {**DEFAULTS, **self.config.get("DRAMATIQ", {})}
        self.broker = broker

        if not isinstance(broker, RedisBroker):
            raise NotImplementedError(
                "judoscale-dramatiq only supports the Redis broker"
            )

        self.redis = broker.client
        logger.debug(f"Redis is at {self.redis.connection_pool}")
        logger.debug(f"Found initial queues: {list(self.queues)}")

    @property
    def adapter_config(self):
        return self.config["DRAMATIQ"]

    @property
    def _queues(self) -> List[str]:
        return list(self.broker.get_declared_queues())

    def oldest_message_timestamp(self, queue: str) -> Optional[float]:
        """
        Get the message_timestamp of the oldest message in the queue.

        Dramatiq stores messages as JSON in Redis lists. The oldest message
        is at the end of the list (RPUSH on enqueue, LPOP on dequeue).
        """
        try:
            redis_key = f"dramatiq:{queue}"
            if payload := self.redis.lindex(redis_key, -1):
                message = json.loads(payload)
                # Dramatiq's message_timestamp is in milliseconds
                if message_ts := message.get("message_timestamp"):
                    return message_ts / 1000.0
        except Exception as e:
            logger.warning(f"Unable to get message from queue: {queue}", exc_info=e)
        return None

    def collect(self) -> List[Metric]:
        metrics = []
        if not self.should_collect:
            return metrics

        logger.debug(f"Collecting metrics for queues {list(self.queues)}")

        for queue in self.queues:
            if timestamp := self.oldest_message_timestamp(queue):
                metrics.append(
                    Metric.for_queue(queue_name=queue, oldest_job_ts=timestamp)
                )
            else:
                metrics.append(
                    Metric.for_queue(queue_name=queue, oldest_job_ts=time.time())
                )

        return metrics
