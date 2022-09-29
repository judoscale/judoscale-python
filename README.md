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
- [ ] Flask
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

Customize Judoscale options in `settings.py` (optional):

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

Add Judoscale options in the app's `settings.py` or `config.py` (optional):

```python
JUDOSCALE = {                                                               
    # API_BASE_URL defaults to ENV["JUDOSCALE_URL"], which is set for you when you install Judoscale.
    "API_BASE_URL": "https://judoscale-python.requestcatcher.com",          
    "LOG_LEVEL": "DEBUG",                                                   
    # REPORT_INTERVAL_SECONDS defaults to 10 seconds.
    "REPORT_INTERVAL_SECONDS": 2,                                           
}
```

Retrieve the above dictionary from the flask app's configuration, e.x from `settings.py` or `config.py`, and merge it with Judoscale's configuration:
For example if the flask app's settings are in a form of an object then do the following:
```python
judoconfig.merge(getattr(config_obj, "JUDOSCALE", {}))
```

## Development

This repo inclues a `sample-apps` directory containing apps you can run locally. These apps use the judoscale-python adapter, but they override `API_BASE_URL` so they're not connected to the real Judoscale API. Instead, they post API requests to https://requestcatcher.com so you can observe the API behavior.

See the `README` in a sample app for details on how to set it up and run locally.
