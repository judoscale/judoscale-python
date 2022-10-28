from celery import Celery
from datetime import datetime as dt


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
#    def __init__(self, celery_app, verbose_logging=False):
    def __init__(self, celery_app):
        self._app = celery_app
        self._state = celery_app.events.State()
        self._logger = EventLogger()
#        self._verbose_logging = verbose_logging
        self.task_started = {}
        self.task_created = {}

    def announce_task_received(self, event):
        self._state.event(event)
        task = self._state.tasks.get(event["uuid"])
        self.task_created[task.uuid] = task.timestamp
        print("TASK ADDED IN QUEUE", task.timestamp)
        print("TASK TIMESTAMPS DICT ", self.task_created)
        self._logger.log_task_status_change(task, event)

    def announce_task_started(self, event):
        self._state.event(event)
        task = self._state.tasks.get(event["uuid"])
        self.task_started[task.uuid] = task.timestamp
        print("TASK STARTED TO BE PROCESSED", task.timestamp)
        self._logger.log_task_status_change(task, event)

    def announce_task_succeeded(self, event):
        self._state.event(event)
        task = self._state.tasks.get(event["uuid"])
        print("WAIT TIME IN QUEUE",
              self.task_started[task.uuid] - self.task_created[task.uuid])
        self._logger.log_task_status_change(task, event)

    def announce_failed_tasks(self, event):
        self._state.event(event)
        # task name is sent only with -received event, and state
        # will keep track of this for us.
        task = self._state.tasks.get(event["uuid"])

        print("TASK FAILED: %s[%s] %s" % (
            task.name, task.uuid, task.info(),))

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
    app = Celery(broker='pyamqp://guest@localhost')

    events_handler = CeleryEventsHandler(app)
    events_handler.start_listening()


