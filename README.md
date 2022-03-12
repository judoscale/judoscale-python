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

### Using Judoscale with Django

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
    # LOG_LEVEL defaults to ENV["LOG_LEVEL"] or "INFO"
    'LOG_LEVEL': 'DEBUG',

    # API_BASE_URL defaults to ENV["JUDOSCALE_URL"], set during add-on installation
    'API_BASE_URL': 'https://example.com',

    # REPORT_INTERVAL_SECONDS defaults to 10 seconds
    'REPORT_INTERVAL_SECONDS': 5,
}
```

## Supported job processors

- [ ] Celery
- [ ] RQ
