JUDOSCALE = {
    "API_BASE_URL": "https://requestinspector.com/inspect/judoscale-fastapi-celery",
    "LOG_LEVEL": "DEBUG",
    "REPORT_INTERVAL_SECONDS": 15,
    # Same as default settings in Config.DEFAULTS
    "CELERY": {
        "ENABLED": True,
        "MAX_QUEUES": 20,
        "QUEUES": [],
    },
}
