import json
import logging
from typing import List, Set

import redis.exceptions
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
        super().__init__(config=config)

    @property
    def queues(self) -> Set[str]:
        return {
            queue.decode() if type(queue) is bytes else queue
            for queue in set(self.redis.keys("[^_]*")) - {b"unacked", b"unacked_index"}
        }

    def collect(self) -> List[Metric]:
        metrics = []
        if self.should_collect:
            for queue in self.queues:
                try:
                    if payload := self.redis.lindex(queue, -1):
                        task = json.loads(payload)
                        if published_at := task["properties"].get("published_at"):
                            metrics.append(
                                Metric.for_queue(
                                    queue_name=queue, oldest_job_ts=published_at
                                )
                            )
                except redis.exceptions.ResponseError as e:
                    logging.warning(
                        f"Unable to get a task from queue: {queue}", exc_info=e
                    )

        return metrics
