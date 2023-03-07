import sys

from app.app import create_app
from rq.worker import Worker

app = create_app()
queues = sys.argv[1:]

# Instantiate a worker with the queues you want to consume from
# and the connection to Redis.
# In this example, we're using the Redis connection that
# we established in the app factory.
#
worker = Worker(queues, connection=app.redis)

# Run the worker *in the app context* which will
# 1. Ensure that the worker has access to the app context; and
# 2. Set up the Judoscale adapter.
#
with app.app_context():
    worker.work()
