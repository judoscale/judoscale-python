# judoscale-python

Official Python adapter for Judoscale—the advanced autoscaler for Heroku

## Installation

```
pip install judoscale-python
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
    'LOG_LEVEL': 'DEBUG',

    # API_BASE_URL defaults to ENV["JUDOSCALE_URL"], which is set for you when you install Judoscale.
    # This is only exposed for testing purposes.
    'API_BASE_URL': 'https://example.com',

    # REPORT_INTERVAL_SECONDS defaults to 10 seconds.
    'REPORT_INTERVAL_SECONDS': 5,
}
```

Once deployed, you will see your "request queue time" metrics available in the Judoscale UI.
