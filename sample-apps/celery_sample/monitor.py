from celery import current_app

from judoscale.celery.tasks_monitor import CeleryEventsHandler


events_handler = CeleryEventsHandler(current_app)
events_handler.start_listening()
