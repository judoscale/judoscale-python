import os

JUDOSCALE = {
    "API_BASE_URL": os.getenv(
        "JUDOSCALE_URL", "https://judoscale-python.requestcatcher.com"
    ),
    "LOG_LEVEL": "DEBUG",
    "DRAMATIQ": {
        "ENABLED": True,
        "MAX_QUEUES": 20,
        "QUEUES": [],
    },
}
