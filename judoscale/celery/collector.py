import json
import time
from threading import Thread
from typing import List, Optional, Set

from celery import Celery
from kombu import Connection
from redis import Redis

from judoscale.core.config import Config
from judoscale.core.logger import logger
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import JobMetricsCollector

DEFAULTS = {
    "ENABLED": True,
    "MAX_QUEUES": 20,
    "QUEUES": [],
}


class TaskSentHandler(Thread):
    def __init__(
        self,
        collector: "CeleryMetricsCollector",
        connection: Connection,
        *args,
        **kwargs,
    ):
        self.collector = collector
        self.connection = connection
        super().__init__(*args, daemon=True, **kwargs)

    def task_sent(self, event):
        self.collector._celery_queues.add(event["queue"])

    def run(self):
        logger.debug("Starting TaskSentHandler")
        recv = self.collector.broker.events.Receiver(
            self.connection,
            handlers={"task-sent": self.task_sent},
        )
        recv.capture(wakeup=False)


class CeleryMetricsCollector(JobMetricsCollector):
    def __init__(self, config: Config, broker: Celery):
        super().__init__(config=config)

        self.config["CELERY"] = {**DEFAULTS, **self.config.get("RQ", {})}

        self.broker = broker
        connection = self.broker.connection_for_read()
        if connection.transport.driver_name != "redis":
            raise NotImplementedError(
                f"Unsupported broker: {connection.transport.driver_name}"
            )

        self.redis: Redis = connection.channel().client

        if not self.is_supported_redis_version:
            raise RuntimeError(
                "Unsupported Redis server version. Minimum Redis version is 6.0."
            )

        self._celery_queues: Set[str] = set()
        self.task_sent_handler = TaskSentHandler(self, connection)
        logger.debug(f"Redis is at {self.redis.connection_pool}")

        system_queues = {"unacked", "unacked_index"}
        user_queues = {
            q.decode("utf-8") if type(q) is bytes else q
            for q in self.redis.scan_iter(match="[^_]*", _type="list")
        }
        logger.debug(f"Found initial queues: {list(user_queues)}")
        self._celery_queues = user_queues - system_queues
        self.task_sent_handler.start()

    @property
    def is_supported_redis_version(self):
        major_version = int(self.redis.info()["redis_version"].split(".")[0])
        return major_version >= 6

    @property
    def adapter_config(self):
        return self.config["CELERY"]

    @property
    def _queues(self) -> List[str]:
        return list(self._celery_queues)

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
            else:
                metrics.append(
                    Metric.for_queue(queue_name=queue, oldest_job_ts=time.time())
                )

        return metrics
