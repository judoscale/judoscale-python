import logging
from datetime import datetime as dt
#from celery import Celery
from celery import current_app

from judoscale.core.metric import Metric
from judoscale.core.reporter import reporter
from judoscale.core.metrics_store import metrics_store

logger = logging.getLogger(__name__)


class EventLogger:
    def log_task_status_change(self, task, event):
        print('[{}] {} {} (STATE={}, UUID={})'.format(
            self._to_datetime(task.timestamp),
            event['type'].upper(),
            task.name,
            task.state.upper(),
            task.uuid
        ))
    def _to_datetime(self, timestamp):
        return dt.fromtimestamp(timestamp) if timestamp is not None else None


class CeleryEventsHandler:
    def __init__(self, celery_app, verbose_logging=False):
        self._app = celery_app
        self._state = celery_app.events.State()
        self._logger = EventLogger()
        self._verbose_logging = verbose_logging
        self.task_started = {}
        self.task_created = {}

    def announce_task_received(self, event):
        self._state.event(event)
        task = self._state.tasks.get(event["uuid"])
        self.task_created[task.uuid] = task.timestamp
        self._logger.log_task_status_change(task, event)
        now = dt.now()
        current_timestamp_ms = now.timestamp()
        queue_time_ms = (
            self.task_created[task.uuid] - current_timestamp_ms) * 1000
        metric = Metric(
            measurement="queue_time",
            datetime=dt.fromtimestamp(self.task_created[task.uuid]),
            value=queue_time_ms
        )
        logger.debug("queue_time={}ms".format(round(queue_time_ms, 2)))
        if metric:
            metrics_store.add_queue(metric)
        reporter.ensure_running()

    def announce_task_started(self, event):
        self._state.event(event)
        task = self._state.tasks.get(event["uuid"])
        self.task_started[task.uuid] = task.timestamp
        self._logger.log_task_status_change(task, event)

    def announce_failed_tasks(self, event):
        self._state.event(event)
        # task name is sent only with -received event, and state
        # will keep track of this for us.
        task = self._state.tasks.get(event["uuid"])

        print("TASK FAILED: %s[%s] %s" % (
            task.name, task.uuid, task.info(),))

    def announce_task_succeeded(self, event):
        self._state.event(event)
        task = self._state.tasks.get(event["uuid"])
        print("WAIT TIME IN QUEUE",
              self.task_started[task.uuid] - self.task_created[task.uuid])
        self._logger.log_task_status_change(task, event)

    def start_listening(self):
        with self._app.connection() as connection:
            recv = self._app.events.Receiver(connection, handlers={
                "task-received": self.announce_task_received,
                "task-started": self.announce_task_started,
                "task-succeeded": self.announce_task_succeeded,
                "task-failed": self.announce_failed_tasks,
            })
            recv.capture(limit=None, timeout=None, wakeup=True)


if __name__ == '__main__':
    events_handler = CeleryEventsHandler(current_app)
    events_handler.start_listening()
