import time

from celery import Celery
from celery import __version__ as celery_version
from celery.signals import before_task_publish

from judoscale.celery.collector import CeleryMetricsCollector
from judoscale.core.adapter import Adapter, AdapterInfo
from judoscale.core.config import config as judoconfig
from judoscale.core.reporter import reporter


@before_task_publish.connect
def before_publish(*args, properties={}, **kwargs):
    properties["published_at"] = time.time()


def judoscale_celery(celery: Celery, extra_config: dict = {}) -> None:
    celery.conf.task_send_sent_event = True

    judoconfig.merge(extra_config)
    collector = CeleryMetricsCollector(config=judoconfig, broker=celery)
    adapter = Adapter(
        identifier="judoscale-celery",
        adapter_info=AdapterInfo(platform_version=celery_version),
        metrics_collector=collector,
    )

    reporter.add_adapter(adapter)
    reporter.ensure_running()
