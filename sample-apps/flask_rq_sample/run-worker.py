import sys

from app.settings import BaseConfig
from redis import Redis

from judoscale.rq.worker import Worker

connection = Redis()
queues = sys.argv[1:]


if __name__ == "__main__":
    worker = Worker(queues, connection=connection)
    worker.start_reporter(extra_config=BaseConfig.JUDOSCALE)
    worker.work(with_scheduler=True)
