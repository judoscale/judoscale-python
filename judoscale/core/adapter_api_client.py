import logging

import requests

from judoscale.core.config import config

logger = logging.getLogger(__name__)


class AdapterApiClient:
    def post_report(self, report):
        try:
            url_metrics = f"{config.api_base_url}/v3/reports"
            metrics_length = len(report["metrics"])
            pid = report["pid"]
            logger.debug(
                f"Posting {metrics_length} metrics from {pid} "
                f"to Judoscale adapter API {url_metrics}"
            )
            requests.post(url_metrics, timeout=5, json=report)
        except requests.RequestException as e:
            logger.warning("Adapter API request failed - {}".format(e))


api_client = AdapterApiClient()
