# judoscale-python

This is the official Python adapter for [Judoscale](https://elements.heroku.com/addons/judoscale). You can use Judoscale without it, but this gives you request queue time metrics and job queue time (for supported job processors).

## Installation

Add judoscale-python to your <code>requirements.txt</code> file:

```
judoscale-python >= 1.0.0rc1
```

Then run this from a terminal to install the package:

```sh
pip install -r requirements.txt
```

## Supported web frameworks

- [x] Django
- [x] Flask
- [ ] FastAPI

## Supported job processors

- [ ] Celery
- [ ] RQ

## Using Judoscale with Django

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

Import `RequestQueueTimeMiddleware` and wrap `wsgi_app`:

```python
# app.py
from judoscale.flask.middleware import RequestQueueTimeMiddleware

app = Flask("MyFlaskApp")
app.wsgi_app = RequestQueueTimeMiddleware(app.wsgi_app)
```

This sets up the Judoscale middleware to capture request queue times.

Optionally, you can customize Judoscale options in the app's `settings.py` or `config.py`:

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

If you do this, you'll need to retrieve the above dictionary from the flask app's configuration and merge it with Judoscale's configuration. For example, if the flask app's settings are in a form of an object, you can do the following:

```python
from judoscale.core.config import config as judoconfig

judoconfig.merge(getattr(config_obj, "JUDOSCALE", {}))
```

Note the [official recomendations for configuring Flask](https://flask.palletsprojects.com/en/2.2.x/config/#configuration-best-practices).

## Using Judoscale with Celery and Django
This brief how-to, uses Redis as a result backend, and RabbitMQ as transport broker.
Install celery and redis with pip
```
$ pip install "celery[redis]
```
Next you need to install RabbitMQ and redis for your system. 
```
$ sudo apt-get install rabbitmq-server
$ sudo apt-get install redis-server
```
and make sure those are running with

```
$ systemctl status rabbitmq-server.service
$ sudo systemctl status redis-server.service
```
For extra information, see [RabbitMQ Get Started](https://www.rabbitmq.com/download.html)
And for how to use it, check [Celery's rabbitmq section](https://docs.celeryq.dev/en/stable/getting-started/backends-and-brokers/rabbitmq.html)
ref [Celery Get Started](https://docs.celeryq.dev/en/stable/getting-started/introduction.html#installation)

Configure your django application with Celery.
Check the `celery_sample/celery_sample/celery.py` for how to import and configure Celery.
Also a sample task can be found under `celery_sample/blog`.

For an extensive how-to:

[Celery official docs about working with Django]( https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html)
	
Run Celery with:
```
$ celery -A celery_sample worker --loglevel=INFO -Q celery -E
```
For more details about Celery, visit the `README` inside the `sample_apps/celery_sample` directory.

## Development

This repo inclues a `sample-apps` directory containing apps you can run locally. These apps use the judoscale-python adapter, but they override `API_BASE_URL` so they're not connected to the real Judoscale API. Instead, they post API requests to https://requestcatcher.com so you can observe the API behavior.

See the `README` in a sample app for details on how to set it up and run locally.
