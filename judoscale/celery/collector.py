import json
import logging
from typing import List, Optional, Set

from celery import Celery
from redis import Redis

from judoscale.core.config import Config
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import JobMetricsCollector

logger = logging.getLogger(__name__)


class CeleryMetricsCollector(JobMetricsCollector):
    def __init__(self, config: Config, broker: Celery):
        connection = broker.connection_for_read()
        if connection.transport.driver_name != "redis":
            raise NotImplementedError(
                f"Unsupported broker: {connection.transport.driver_name}"
            )

        self.redis: Redis = connection.channel().client
        self.queues: Set[str] = set()
        logger.debug(f"Redis is at {self.redis.connection_pool}")
        super().__init__(config=config)

    def oldest_task(self, queue: str) -> Optional[dict]:
        """
        Get the oldest task from the queue.
        """
        try:
            if payload := self.redis.lindex(queue, -1):
                return json.loads(payload)
        except Exception as e:
            logger.warning(f"Unable to get a task from queue: {queue}", exc_info=e)
        return None

    def collect(self) -> List[Metric]:
        metrics = []
        if not self.should_collect:
            return metrics

        logger.debug(f"Collecting metrics for queues {list(self.queues)}")
        for queue in self.queues:
            if task := self.oldest_task(queue):
                if published_at := task["properties"].get("published_at"):
                    metrics.append(
                        Metric.for_queue(queue_name=queue, oldest_job_ts=published_at)
                    )

        return metrics
