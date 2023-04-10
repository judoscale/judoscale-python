import time
from datetime import timezone
from typing import List, Optional

from redis import Redis
from rq import Queue
from rq.job import Job

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


class RQMetricsCollector(JobMetricsCollector):
    def __init__(self, config: Config, redis: Redis):
        super().__init__(config=config)

        self.config["RQ"] = {**DEFAULTS, **self.config.get("RQ", {})}
        self.redis: Redis = redis
        logger.debug(f"Redis is at {self.redis.connection_pool}")
        logger.debug(f"Found initial queues: {list(self.queues)}")

    @property
    def adapter_config(self):
        return self.config["RQ"]

    @property
    def _queues(self) -> List[str]:
        return [q.name for q in Queue.all(connection=self.redis)]

    def oldest_job(self, queue: Queue) -> Optional[Job]:
        """
        Get the oldest task from the queue.
        """
        try:
            if jobs := queue.get_jobs(offset=0, length=1):
                return jobs[0]
        except Exception as e:
            logger.warning(f"Unable to get a task from queue: {queue.name}", exc_info=e)
        return None

    def collect(self) -> List[Metric]:
        metrics = []
        if not self.should_collect:
            return metrics

        logger.debug(f"Collecting metrics for queues {list(self.queues)}")
        queues = [Queue(name=q, connection=self.redis) for q in self.queues]

        for queue in queues:
            if self.adapter_config["TRACK_BUSY_JOBS"]:
                metrics.append(
                    Metric.for_busy_queue(
                        queue_name=queue.name,
                        busy_jobs=queue.started_job_registry.count,
                    )
                )

            if job := self.oldest_job(queue):
                if job.enqueued_at is not None:
                    # RQ stores `enqueued_at` as a naive datetime object, which
                    # means it doesn't have any timezone information associated
                    # with it.
                    # But since the time is, in fact, in UTC, we can just replace
                    # the timezone with UTC and then convert it to a timestamp.
                    # https://github.com/rq/rq/blob/42ac7d4150951b5f5fba8be11573920c1e6f6e69/rq/queue.py#L1003
                    #
                    enqueued_at = job.enqueued_at.replace(
                        tzinfo=timezone.utc
                    ).timestamp()

                    metrics.append(
                        Metric.for_queue(
                            queue_name=queue.name, oldest_job_ts=enqueued_at
                        )
                    )
            else:
                metrics.append(
                    Metric.for_queue(queue_name=queue.name, oldest_job_ts=time.time())
                )

        return metrics
