import random
import time

import dramatiq
from dramatiq.brokers.redis import RedisBroker

import app.settings as settings
from judoscale.dramatiq import judoscale_dramatiq

broker = RedisBroker(url="redis://localhost:6379/0")
dramatiq.set_broker(broker)

judoscale_dramatiq(broker, extra_config=settings.JUDOSCALE)


@dramatiq.actor(queue_name="low")
def add_low(x, y):
    time.sleep(random.randint(3, 5))
    _ = x + y


@dramatiq.actor(queue_name="high")
def add_high(x, y):
    time.sleep(random.randint(3, 5))
    _ = x + y
