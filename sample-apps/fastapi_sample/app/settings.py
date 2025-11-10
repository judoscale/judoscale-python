import os

JUDOSCALE = {
    "API_BASE_URL": os.getenv(
        "JUDOSCALE_URL", "https://judoscale-python.requestcatcher.com"
    ),
    "LOG_LEVEL": "DEBUG",
    # "REPORT_INTERVAL_SECONDS": 5
}
