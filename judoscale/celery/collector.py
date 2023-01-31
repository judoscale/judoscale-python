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
        logger.debug(f"Redis is at {self.redis.connection_pool.connection_kwargs}")
        super().__init__(config=config)

    @property
    def queues(self) -> Set[str]:
        """
        Get all queues from Redis.
        """
        system_queues = {"unacked", "unacked_index"}
        queues = set(self.redis.scan_iter(match="[^_]*", _type="list"))
        queues = {queue.decode() if type(queue) is bytes else queue for queue in queues}
        return queues - system_queues

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

        for queue in self.queues:
            if task := self.oldest_task(queue):
                if published_at := task["properties"].get("published_at"):
                    metrics.append(
                        Metric.for_queue(queue_name=queue, oldest_job_ts=published_at)
                    )

        return metrics
