from judoscale.core.config import config
import logging
import requests
import json

logger = logging.getLogger(__name__)


class AdapterApiClient:
    def post_report(self, report):
        try:
            url_metrics = config.api_base_url + "/v1/metrics"
            logger.debug(
                f"Posting metrics {report} to Judoscale adapter API {url_metrics}")
            requests.post(url_metrics, timeout=5, json=report)
        except requests.RequestException as e:
            logger.warning("Adapter API request failed - {}".format(e))


api_client = AdapterApiClient()
