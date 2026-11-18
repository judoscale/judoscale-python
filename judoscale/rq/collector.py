import time
from datetime import timezone
from typing import List, Optional, Tuple

from redis import Redis
from rq import Queue
from rq.job import Job
from rq.utils import utcparse

from judoscale.core.config import Config
from judoscale.core.logger import logger
from judoscale.core.metric import Metric
from judoscale.core.metrics_collectors import JobMetricsCollector

DEFAULTS = {
    "ENABLED": True,
    "MAX_QUEUES": 20,
    "QUEUES": [],
    "TRACK_BUSY_JOBS": True,
}


class RQMetricsCollector(JobMetricsCollector):
    def __init__(self, config: Config, redis: Redis):
        super().__init__(config=config)

        self.config["RQ"] = {**DEFAULTS, **self.config.get("RQ", {})}
        self.redis: Redis = redis
        logger.debug(f"Redis is at {self.redis.connection_pool}")

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

    def _queue_depth(self, queue: Queue) -> Optional[int]:
        try:
            return int(queue.count)
        except Exception as e:
            logger.warning(
                f"Unable to get queue depth for queue: {queue.name}", exc_info=e
            )
            return None

    def _busy_jobs(self, queue: Queue) -> Optional[Tuple[int, Optional[float]]]:
        """
        Get the number of jobs being processed for the queue, and when the
        longest-running one started (a Unix timestamp, or None).
        """
        # `StartedJobRegistry.count` runs `cleanup()` first, which writes to
        # Redis (moving abandoned jobs to the failed registry). Read only the
        # unexpired entries instead, which gives the same jobs read-only.
        try:
            registry = queue.started_job_registry
            entries = self.redis.zrangebyscore(registry.key, f"({time.time()}", "+inf")
            pipeline = self.redis.pipeline()
            for entry in entries:
                # RQ 2 stores `<job_id>:<execution_id>` entries, RQ 1 job IDs.
                job_id = entry.decode().split(":")[0]
                pipeline.hget(Job.key_for(job_id), "started_at")
            # RQ 1 parses to a naive datetime, though the time is in UTC.
            started_ats = [
                utcparse(started_at.decode()).replace(tzinfo=timezone.utc).timestamp()
                for started_at in pipeline.execute()
                if started_at
            ]
            return len(entries), min(started_ats, default=None)
        except Exception as e:
            logger.warning(
                f"Unable to get busy jobs for queue: {queue.name}", exc_info=e
            )
            return None

    def collect(self) -> List[Metric]:
        metrics = []
        if not self.should_collect:
            return metrics

        queue_names = self.queues
        logger.debug(f"Collecting metrics for queues {list(queue_names)}")
        queues = [Queue(name=q, connection=self.redis) for q in queue_names]

        for queue in queues:
            if (
                self.adapter_config["TRACK_BUSY_JOBS"]
                and (busy := self._busy_jobs(queue)) is not None
            ):
                busy_jobs, oldest_job_start_ts = busy
                metrics.append(
                    Metric.for_busy_queue(queue_name=queue.name, busy_jobs=busy_jobs)
                )
                metrics.append(
                    Metric.for_busy_time(
                        queue_name=queue.name, oldest_job_start_ts=oldest_job_start_ts
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

            if (depth := self._queue_depth(queue)) is not None:
                metrics.append(
                    Metric.for_queue_depth(queue_name=queue.name, depth=depth)
                )

        return metrics
