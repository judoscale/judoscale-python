import json
import time
from datetime import datetime
from collections import defaultdict
from threading import Thread
from typing import List, Optional, Set, Tuple

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
    "TRACK_BUSY_JOBS": False,
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

        self.config["CELERY"] = {**DEFAULTS, **self.config.get("CELERY", {})}

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

        if self.adapter_config["TRACK_BUSY_JOBS"]:
            self.inspect = broker.control.inspect(connection=connection)

        self._celery_queues: Set[str] = set()
        self.task_sent_handler = TaskSentHandler(self, connection)
        logger.debug(f"Redis is at {self.redis.connection_pool}")

        system_queues = {"unacked", "unacked_index"}
        for q in self.redis.scan_iter(_type="list"):
            queue_name = q.decode() if isinstance(q, bytes) else q
            if (
                queue_name in system_queues
                or queue_name.startswith("_kombu")
                or queue_name.endswith("celery.pidbox")
            ):
                continue
            self._celery_queues.add(queue_name)

        logger.debug(f"Found initial queues: {list(self._celery_queues)}")
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

    def oldest_task_and_timestamp(
        self, queue: str
    ) -> Optional[Tuple[dict, Optional[float]]]:
        """
        Get the oldest task from the queue, alongside the timestamp to be used for latency.

        When a task contains no `eta`, we use the `published_at` timestamp we inject;
        When a task contains a past `eta`, we use it instead of `published_at`;
        When a task contains a future `eta`, we skip that task and continue looking through tasks in the queue.
        """
        try:
            last_index = -1
            now = time.time()

            while payload := self.redis.lindex(queue, last_index):
                payload = json.loads(payload)

                if eta := payload.get("headers", {}).get("eta"):
                    eta = datetime.fromisoformat(eta).timestamp()

                    if eta <= now:
                        return payload, eta
                    else:
                        last_index = last_index - 1
                elif published_at := payload.get("properties", {}).get("published_at"):
                    return payload, published_at
                else:
                    return payload, None

        except Exception as e:
            logger.warning(f"Unable to get a task from queue: {queue}", exc_info=e)

        return None

    def collect(self) -> List[Metric]:
        metrics = []
        if not self.should_collect:
            return metrics

        if self.adapter_config["TRACK_BUSY_JOBS"]:
            busy_counts = defaultdict(lambda: 0)
            if workers_tasks := self.inspect.active():
                for active_tasks in workers_tasks.values():
                    for task in active_tasks:
                        busy_counts[task["delivery_info"]["routing_key"]] += 1

            for queue in self.queues:
                count = busy_counts[queue]
                metrics.append(Metric.for_busy_queue(queue_name=queue, busy_jobs=count))

        logger.debug(f"Collecting metrics for queues {list(self.queues)}")
        for queue in self.queues:
            if result := self.oldest_task_and_timestamp(queue):
                task, timestamp = result
                if timestamp:
                    metrics.append(
                        Metric.for_queue(queue_name=queue, oldest_job_ts=timestamp)
                    )
                else:
                    task_id = task.get("id", None)
                    logger.warning(
                        "Unable to find `published_at` in task properties for "
                        f"task ID {task_id} in queue {queue}."
                    )
            else:
                metrics.append(
                    Metric.for_queue(queue_name=queue, oldest_job_ts=time.time())
                )

        return metrics
