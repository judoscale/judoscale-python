# Judoscale

This is the official Python adapter for [Judoscale](https://elements.heroku.com/addons/judoscale). You can use Judoscale without it, but this gives you request queue time metrics and job queue time (for supported job processors).

It is recommended to install the specific web framework and/or background job library support as "extras" to the `judoscale` PyPI package. This ensures that checking if the installed web framework and/or background task processing library is supported happens at dependency resolution time.

## Supported web frameworks

- [x] [Django](#using-judoscale-with-django)
- [x] [Flask](#using-judoscale-with-flask)
- [ ] FastAPI

## Supported job processors

- [x] [Celery](#using-judoscale-with-celery-and-redis) (with Redis as the broker)
- [ ] RQ

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
    # LOG_LEVEL defaults to ENV["LOG_LEVEL"] or "INFO".
    "LOG_LEVEL": "DEBUG",

    # API_BASE_URL defaults to ENV["JUDOSCALE_URL"], which is set for you when you install Judoscale.
    # This is only exposed for testing purposes.
    "API_BASE_URL": "https://example.com",

    # REPORT_INTERVAL_SECONDS defaults to 10 seconds.
    "REPORT_INTERVAL_SECONDS": 5,
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
    # LOG_LEVEL defaults to ENV["LOG_LEVEL"] or "INFO".
    "LOG_LEVEL": "DEBUG",

    # API_BASE_URL defaults to ENV["JUDOSCALE_URL"], which is set for you when you install Judoscale.
    # This is only exposed for testing purposes.
    "API_BASE_URL": "https://example.com",

    # REPORT_INTERVAL_SECONDS defaults to 10 seconds.
    "REPORT_INTERVAL_SECONDS": 5,
}
```

Note the [official recommendations for configuring Flask](https://flask.palletsprojects.com/en/2.2.x/config/#configuration-best-practices).

# Using Judoscale with Celery and Redis

Install Judoscale for Celery with:

```sh
$ pip install 'judoscale[celery-redis]'
```

> **NOTE 1:** The Judoscale Celery integration currently only works with the [Redis broker](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/index.html#redis).

> **NOTE 2:** Using [task priorities](https://docs.celeryq.dev/en/latest/userguide/calling.html#advanced-options) is currently not supported by `judoscale`. You can still use task priorities, but `judoscale` won't see and report metrics on any queues other than the default, unprioritised queue.

Judoscale can automatically scale the number of Celery workers based on the queue latency (the age of the oldest pending task in the queue).

To use the Celery integration, import `judoscale_celery` and call it with the Celery app instance. `judoscale_celery` should be called after you have set up and configured the Celery instance.

```py
from celery import Celery
from judoscale.celery import judoscale_celery

broker = Celery("Broker", broker="redis://localhost:6379/0")
# Further setup
# broker.conf.update(...)
# ...

judoscale_celery(broker)
```

This sets up Judoscale to periodically calculate and report queue latency for each Celery queue.

If you need to change the Judoscale integration configuration, you can pass a dictionary of Judoscale configuration options to `judoscale_celery` to override the default Judoscale config variables:

```py
judoscale_celery(broker, extra_config={"LOG_LEVEL": "DEBUG"})
```

## Development

This repo includes a `sample-apps` directory containing apps you can run locally. These apps use the `judoscale` adapter, but they override `API_BASE_URL` so they're not connected to the real Judoscale API. Instead, they post API requests to https://requestcatcher.com so you can observe the API behavior.

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
$ python -m unittest discover -s tests
```
