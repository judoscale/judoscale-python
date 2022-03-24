from judoscale.core.config import config
import logging
import requests
import json

logger = logging.getLogger(__name__)


class AdapterApiClient:
    def post_report(self, report):
        try:
            logger.debug("Posting metrics to Judoscale adapter API")
            requests.post(config.api_base_url + "/v1/metrics", timeout=5, json=report)
        except requests.RequestException as e:
            logger.warn("Adapter API request failed - {}".format(e))


api_client = AdapterApiClient()
