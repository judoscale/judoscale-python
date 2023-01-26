import time

from celery import Celery
from celery.signals import before_task_publish

from judoscale.celery.collector import CeleryMetricsCollector
from judoscale.core.config import config as judoconfig
from judoscale.core.reporter import reporter


@before_task_publish.connect
def before_publish(*args, properties={}, **kwargs):
    properties["published_at"] = time.time()


def judoscale_celery(celery: Celery, extra_config: dict) -> None:
    judoconfig.merge(extra_config)
    collector = CeleryMetricsCollector(config=judoconfig, broker=celery)
    reporter.add_collector(collector)
    reporter.ensure_running()
