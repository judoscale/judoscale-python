import json
import logging
from typing import List, Set

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
        keys = set(self.redis.keys("[^_]*")) - {b"unacked", b"unacked_index"}
        pipe = self.redis.pipeline()
        for key in keys:
            pipe.type(key)
        key_types = zip(keys, pipe.execute())
        queues = [key for key, type_ in key_types if type_ in {b"list", "list"}]
        return {queue.decode() if type(queue) is bytes else queue for queue in queues}

    def oldest_task(self, queue: str) -> dict | None:
        """
        Get the oldest task from the queue.
        """
        try:
            if payload := self.redis.lindex(queue, -1):
                return json.loads(payload)
        except Exception as e:
            logging.warning(f"Unable to get a task from queue: {queue}", exc_info=e)
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
