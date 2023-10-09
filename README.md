# Judoscale

This is the official Python adapter for [Judoscale](https://elements.heroku.com/addons/judoscale). You can use Judoscale without it, but this gives you request queue time metrics and job queue time (for supported job processors).

It is recommended to install the specific web framework and/or background job library support as "extras" to the `judoscale` PyPI package. This ensures that checking if the installed web framework and/or background task processing library is supported happens at dependency resolution time.

## Supported web frameworks

- [x] [Django](#using-judoscale-with-django)
- [x] [Flask](#using-judoscale-with-flask)
- [x] [FastAPI](#using-judoscale-with-fastapi)

## Supported job processors

- [x] [Celery](#using-judoscale-with-celery-and-redis) (with Redis 6.0+ as the broker)
- [x] [RQ](#using-judoscale-with-rq)

# Using Judoscale with Django

Install Judoscale for Django with:

```sh
$ pip install 'judoscale[django]'
```

Add Judoscale app to `settings.py`:

```python
INSTALLED_APPS = [
    "judoscale.django",
    # ... other apps
]
```

This sets up the Judoscale middleware to capture request queue times.

Optionally, you can customize Judoscale in `settings.py`:

```python
JUDOSCALE = {
    # Log level defaults to ENV["LOG_LEVEL"] or "INFO".
    "LOG_LEVEL": "DEBUG",
}
```

Once deployed, you will see your request queue time metrics available in the Judoscale UI.

# Using Judoscale with Flask

Install Judoscale for Flask with:

```sh
$ pip install 'judoscale[flask]'
```

The Flask support for Judoscale is packaged into a Flask extension. Import the extension class and use like you normally would in a Flask application:

```py
# app.py

from judoscale.flask import Judoscale

# If your app is a top-level global

app = Flask("MyFlaskApp")
app.config.from_object('...')  # or however you configure your app
judoscale = Judoscale(app)


# If your app uses the application factory pattern

judoscale = Judoscale()

def create_app():
    app = Flask("MyFlaskApp")
    app.config.from_object('...')  # or however you configure your app
    judoscale.init_app(app)
    return app
```

This sets up the Judoscale extension to capture request queue times.

Optionally, you can override Judoscale's own configuration via your application's [configuration dictionary](https://flask.palletsprojects.com/en/2.2.x/api/#flask.Flask.config). The Judoscale Flask extension looks for a top-level `"JUDOSCALE"` key in `app.config`, which should be a dictionary, and which the extension uses to configure itself as soon as `judoscale.init_app()` is called.

```python
JUDOSCALE = {
    # Log level defaults to ENV["LOG_LEVEL"] or "INFO".
    "LOG_LEVEL": "DEBUG",
}
```

Note the [official recommendations for configuring Flask](https://flask.palletsprojects.com/en/2.2.x/config/#configuration-best-practices).

# Using Judoscale with FastAPI

Install Judoscale for FastAPI with:

```sh
$ pip install 'judoscale[asgi]'
```

Since FastAPI uses [Starlette](https://www.starlette.io/), an ASGI framework, the integration is packaged into [ASGI middleware](https://asgi.readthedocs.io/en/latest/specs/main.html#middleware). Import the middleware class and register it with your FastAPI app:

```py
# app.py

from judoscale.asgi.middleware import FastAPIRequestQueueTimeMiddleware

# If your app is a top-level global

app = FastAPI()
app.add_middleware(FastAPIRequestQueueTimeMiddleware)


# If your app uses the application factory pattern

def create_app():
    app = FastAPI()
    app.add_middleware(FastAPIRequestQueueTimeMiddleware)
    return app
```

This sets up the Judoscale extension to capture request queue times.

Optionally, you can override Judoscale's configuration by passing in extra configuration to the `add_middleware` method:

```py
app.add_middleware(FastAPIRequestQueueTimeMiddleware, extra_config={"LOG_LEVEL": "DEBUG"})
```

## Other ASGI frameworks

Judoscale also provides middleware classes for Starlette and Quart. You can use them with

```py
# For Starlette, if you're using Starlette directly, without FastAPI
from judoscale.asgi.middleware import StarletteRequestQueueTimeMiddleware

# For Quart
from judoscale.asgi.middleware import QuartRequestQueueTimeMiddleware
```

If your app uses a framework for which we have not provided a middleware class, but it implements the [ASGI spec](https://asgi.readthedocs.io/en/latest/specs/index.html), you can easily create your own version of the request queue time middleware.

```py
from judoscale.asgi.middleware import RequestQueueTimeMiddleware

class YourFrameworkRequestQueueTimeMiddleware(RequestQueueTimeMiddleware):
    # NOTE: The `platform` class variable value should be the package name
    # of the web framework you're using. It is used to look up package
    # metadata for reporting back to the Judoscale API.
    platform = "your_framework"
```

Then register `YourFrameworkRequestQueueTimeMiddleware` with your application like you normally would.

# Using Judoscale with Celery and Redis

Install Judoscale for Celery with:

```sh
$ pip install 'judoscale[celery-redis]'
```

> :warning: **NOTE 1:** The Judoscale Celery integration currently only works with the [Redis broker](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/index.html#redis). The minimum supported Redis server version is 6.0.

> :warning: **NOTE 2:** Using [task priorities](https://docs.celeryq.dev/en/latest/userguide/calling.html#advanced-options) is currently not supported by `judoscale`. You can still use task priorities, but `judoscale` won't see and report metrics on any queues other than the default, unprioritised queue.

Judoscale can automatically scale the number of Celery workers based on the queue latency (the age of the oldest pending task in the queue).

## Setting up the integration

To use the Celery integration, import `judoscale_celery` and call it with the Celery app instance. `judoscale_celery` should be called after you have set up and configured the Celery instance.

```py
from celery import Celery
from judoscale.celery import judoscale_celery

celery_app = Celery(broker="redis://localhost:6379/0")
# Further setup
# celery_app.conf.update(...)
# ...

judoscale_celery(celery_app)
```

This sets up Judoscale to periodically calculate and report queue latency for each Celery queue.

If you need to change the Judoscale integration configuration, you can pass a dictionary of Judoscale configuration options to `judoscale_celery` to override the default Judoscale config variables:

```py
judoscale_celery(celery_app, extra_config={"LOG_LEVEL": "DEBUG"})
```

An example configuration dictionary accepted by `extra_config`:

```py
{
    "LOG_LEVEL": "INFO",

    # In addition to global configuration options for the Judoscale
    # integration above, you can also specify the following configuration
    # options for the Celery integration.
    "CELERY": {
        # Enable (default) or disable the Celery integration
        "ENABLED": True,

        # Report metrics on up to MAX_QUEUES queues.
        # The list of discovered queues are sorted by the length
        # of the queue name (shortest first) and metrics are
        # reported for the first MAX_QUEUES queues.
        # Defaults to 20.
        "MAX_QUEUES": 20,

        # Specify a list of known queues to report metrics for.
        # MAX_QUEUES is still honoured.
        # Defaults to empty list (report metrics for discovered queues).
        "QUEUES": [],

        # Enable or disable (default) tracking how many jobs are currently being
        # processed in each queue.
        # This allows Judoscale to avoid downscaling workers that are executing jobs.
        # See documentation: https://judoscale.com/docs/long-running-jobs-ruby#enable-long-running-job-support-in-the-dashboard
        # NOTE: This option requires workers to have unique names. If you are running
        # multiple Celery workers on the same machine, make sure to give each
        # worker a distinct name.
        # More information: https://docs.celeryq.dev/en/stable/userguide/workers.html#starting-the-worker
        "TRACK_BUSY_JOBS": False,
    }
}
```

> :warning: **NOTE:** Calling `judoscale_celery` turns on sending [`task-sent`](https://docs.celeryq.dev/en/stable/userguide/configuration.html#task-send-sent-event) events. This is required for the Celery integration with Judoscale to work.

### Judoscale with Celery and Flask

Depending on how you've structured your Flask app, you should call `judoscale_celery` after your application has finished configuring the Celery app instance. If you have followed the [Flask guide](https://flask.palletsprojects.com/en/2.2.x/patterns/celery/) in the Flask documentation, the easiest place to initialise the Judoscale integration is in the application factory:

```py
def create_app():
    app = Flask(__name__)
    app.config.from_object(...) # or however you configure your app
    celery_app = celery_init_app(app)
    # Initialise the Judoscale integration
    judoscale_celery(celery_app, extra_config=app.config["JUDOSCALE"])
    return app
```

### Judoscale with Celery and Django

If you have followed the [Django guide](https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html) in the Celery documentation, you should have a module where you initialise the Celery app instance, auto-discover tasks, etc. You should call `judoscale_celery` after you have configured the Celery app instance:

```py
from celery import Celery
from django.conf import settings
from judoscale.celery import judoscale_celery

app = Celery()
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
# Initialise the Judoscale integration
judoscale_celery(app, extra_config=settings.JUDOSCALE)
```

# Using Judoscale with RQ

Install Judoscale for RQ with:

```sh
$ pip install 'judoscale[rq]'
```

Judoscale can automatically scale the number of RQ workers based on the queue latency (the age of the oldest pending task in the queue).

## Setting up the integration

To use the RQ integration, import `judoscale_rq` and call it with an instance of `Redis` pointing to the same Redis database that RQ uses.

```py
from redis import Redis
from judoscale.rq import judoscale_rq

redis = Redis(...)
judoscale_rq(redis)
```

This sets up Judoscale to periodically calculate and report queue latency for each RQ queue.

If you need to change the Judoscale integration configuration, you can pass a dictionary of Judoscale configuration options to `judoscale_rq` to override the default Judoscale config variables:

```py
judoscale_rq(redis, extra_config={"LOG_LEVEL": "DEBUG"})
```

An example configuration dictionary accepted by `extra_config`:

```py
 {
    "LOG_LEVEL": "INFO",

    # In addition to global configuration options for the Judoscale
    # integration above, you can also specify the following configuration
    # options for the RQ integration.
    "RQ": {
        # Enable (default) or disable the RQ integration
        "ENABLED": True,

        # Report metrics on up to MAX_QUEUES queues.
        # The list of discovered queues are sorted by the length
        # of the queue name (shortest first) and metrics are
        # reported for the first MAX_QUEUES queues.
        # Defaults to 20.
        "MAX_QUEUES": 20,

        # Specify a list of known queues to report metrics for.
        # MAX_QUEUES is still honoured.
        # Defaults to empty list (report metrics for discovered queues).
        "QUEUES": [],

        # Enable or disable (default) tracking how many jobs are currently being
        # processed in each queue.
        # This allows Judoscale to avoid downscaling workers that are executing jobs.
        # See documentation: https://judoscale.com/docs/long-running-jobs-ruby#enable-long-running-job-support-in-the-dashboard
        "TRACK_BUSY_JOBS": False,
}
```

### Judoscale with RQ and Flask

The recommended way to initialise Judoscale for RQ is in the application factory:

```py
judoscale = Judoscale()

def create_app():
    app = Flask(__name__)
    app.config.from_object("...") # or however you configure your application
    app.redis = Redis()

    # Initialise the Judoscale integration for Flask
    judoscale.init_app(app)

    # Initialise the Judoscale integration for RQ
    judoscale_rq(app.redis)

    return app
```

Then, in your worker script, make sure that you create an app, which will initialise the Judoscale integration with RQ. Although not required, it's useful to run the worker within the Flask app context. If you have followed the [RQ on Heroku pattern](https://python-rq.org/patterns/) for setting up your RQ workers on Heroku, your worker script should look something like this:

```py
from rq.worker import HerokuWorker as Worker

app = create_app()

worker = Worker(..., connection=app.redis)
with app.app_context():
    worker.work()
```

See the [run-worker.py script](./sample-apps/flask_rq_sample/run-worker.py) for reference.

### Judoscale with RQ and Django

The Judoscale integration for RQ is packaged into a separate Django app.

You should already have `judoscale.django` in your `INSTALLED_APPS`. Next, add the RQ integration app `judoscale.rq`:

```python
INSTALLED_APPS = [
    "judoscale.django",
    "judoscale.rq",
    # ... other apps
]
```

By default, `judoscale.rq` will connect to the Redis instance as specified by the `REDIS_URL` environment variable. If that is not suitable, you can supply Redis connection information in the `JUDOSCALE` configuration dictionary under the `"REDIS"` key.

Accepted formats are:

- a dictionary containing a single key `"URL"` pointing to a Redis server URL, or;
- a dictionary of configuration options corresponding to the keyword arguments of the [`Redis` constructor](https://github.com/redis/redis-py/blob/6c708c2e0511364c2c3f21fa1259de05e590632d/redis/client.py#L905).

```py
JUDOSCALE = {
    # Configuring with a Redis server URL
    "REDIS": {
        "URL": os.getenv("REDISTOGO_URL"),
        "SSL_CERT_REQS": None  # If you are running on Heroku and using Heroku Data for Redis Premium
    }

    # Configuring as kwargs to Redis(...)
    "REDIS": {
        "HOST": "localhost",
        "PORT": 6379,
        "DB": 0
        "SSL_CERT_REQS": None  # If you are running on Heroku and using Heroku Data for Redis Premium
    }
}
```

> :warning: **NOTE:** If you are running on Heroku and using any of the Premium plans for Heroku Data for Redis, you will have to turn off SSL certificate verification as per https://help.heroku.com/HC0F8CUS/redis-connection-issues.

If you are using [Django-RQ](https://github.com/rq/django-rq/tree/master), you can also pull configuration from `RQ_QUEUES` directly:

```py
RQ_QUEUES = {
    "high_priority": {
        "HOST": "...",
        "PORT": 6379,
        "DB": 0
    },
}

JUDOSCALE = {
    # ... other configuration options
    "REDIS": RQ_QUEUES["high_priority"]
}
```

> :warning: **NOTE:** Django-RQ enables configuring RQ such that different queues and workers use _different_ Redis instances. Judoscale currently only supports connecting to and monitoring queue latency on a single Redis instance.

## Debugging & troubleshooting

If Judoscale is not recognizing your adapter installation or if you're not seeing expected metrics in Judoscale, you'll want to check the logging output. Here's how you'd do that on Heroku.

First, enable debug logging:

```sh
heroku config:set JUDOSCALE_LOG_LEVEL=debug
```

Then, tail your logs while your app initializes:

```sh
heroku logs --tail | grep Judoscale
```

You should see Judoscale collecting and reporting metrics every 10 seconds from every running process. If the issue is not clear from the logs, email help@judoscale.com for support. Please include any logging you've collected and any other behavior you've observed.

## Development

This repo includes a `sample-apps` directory containing apps you can run locally. These apps use the `judoscale` adapter, but they override `API_BASE_URL` so they're not connected to the real Judoscale API. Instead, they post API requests to https://requestinspector.com so you can observe the API behavior.

See the `README` in a sample app for details on how to set it up and run locally.

### Contributing

`judoscale` uses [Poetry](https://python-poetry.org/) for managing dependencies and packaging the project. Head over to the [installations instructions](https://python-poetry.org/docs/#installing-with-the-official-installer) and install Poetry, if needed.

Clone the repo with

```sh
$ git clone git@github.com:judoscale/judoscale-python.git
$ cd judoscale-python
```

Verify that you are on a recent version of Poetry:

```sh
$ poetry --version
Poetry (version 1.3.1)
```

Install dependencies with Poetry and activate the virtualenv

```sh
$ poetry install --all-extras
$ poetry shell
```

Run tests with

```sh
$ pytest
```
