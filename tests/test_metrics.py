import time
import unittest

from judoscale.core.metric import Metric


class TestMetricsForWeb(unittest.TestCase):
    def test_heroku_metrics(self):
        # Heroku timestamp is in integer milliseconds
        heroku_timestamp = str(round(time.time() * 1000))
        time.sleep(0.05)
        metric = Metric.for_web(heroku_timestamp)
        # Allow metric value to be within 10ms of 50ms to account for
        # the time it takes to run the test.
        self.assertAlmostEqual(metric.value, 50, delta=10)

    def test_nginx_metrics(self):
        # Nginx timestamp is in seconds with millisecond resolution (3dp).
        #
        # NOTE: We manually format to 3dp here because time.time() returns the
        # time in seconds with microsecond resolution (6dp).
        nginx_timestamp = str(f"t={time.time():.3f}")
        time.sleep(0.05)
        metric = Metric.for_web(nginx_timestamp)
        # Allow metric value to be within 10ms of 50ms to account for
        # the time it takes to run the test.
        self.assertAlmostEqual(metric.value, 50, delta=10)
