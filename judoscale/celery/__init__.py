import time

from celery import Celery
from celery.signals import before_task_publish

from judoscale.celery.collector import CeleryMetricsCollector
from judoscale.core.config import config as judoconfig
from judoscale.core.reporter import reporter

before_publish_handler = None


def before_publish(collector: CeleryMetricsCollector):
    def _before_publish(*args, routing_key, properties={}, **kwargs):
        collector.queues.add(routing_key)
        properties["published_at"] = time.time()

    return _before_publish


def judoscale_celery(celery: Celery, extra_config: dict = {}) -> None:
    global before_publish_handler

    judoconfig.merge(extra_config)
    collector = CeleryMetricsCollector(config=judoconfig, broker=celery)

    before_publish_handler = before_task_publish.connect(before_publish(collector))

    reporter.add_collector(collector)
    reporter.ensure_running()
