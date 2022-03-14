from judoscale.core.config import config
import logging
import requests
import json

logger = logging.getLogger(__name__)

class AdapterApiClient:
    def __init__(self):
        pass

    def post_metrics(self, metrics):
        try:
            logger.debug("[Judoscale] Posting metrics to Judoscale adapter API")
            payload = json.dumps(metrics)
            r = requests.post(config.api_base_url + '/adapter/v1/reports', timeout=5, json=payload)
        except:
            logger.debug("TODO: handle API exception")


api_client = AdapterApiClient()
