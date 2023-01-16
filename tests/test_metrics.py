import time
import unittest

from judoscale.core.metric import Metric


class TestMetricsForWeb(unittest.TestCase):
    def test_heroku_metrics(self):
        # Heroku timestamp is in integer milliseconds
        heroku_timestamp = str(round(time.time() * 1000))
        metric = Metric.for_web(heroku_timestamp)
        self.assertAlmostEqual(metric.value, 0, delta=1)

    def test_nginx_metrics(self):
        # Nginx timestamp is in float seconds, in the format "t=123.456"
        nginx_timestamp = str(f"t={time.time()}")
        metric = Metric.for_web(nginx_timestamp)
        self.assertAlmostEqual(metric.value, 0, delta=1)
