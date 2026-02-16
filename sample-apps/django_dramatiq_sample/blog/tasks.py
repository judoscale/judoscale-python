import random
import time

import dramatiq


@dramatiq.actor(queue_name="low")
def add_low(x, y):
    time.sleep(random.randint(3, 5))
    _ = x + y


@dramatiq.actor(queue_name="high")
def add_high(x, y):
    time.sleep(random.randint(3, 5))
    _ = x + y
