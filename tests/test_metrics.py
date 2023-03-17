import time

from pytest import approx

from judoscale.core.metric import Metric


class TestMetricsForWeb:
    def test_heroku_metrics(self):
        # Heroku timestamp is in integer milliseconds
        heroku_timestamp = str(round(time.time() * 1000))
        time.sleep(0.02)
        metric = Metric.for_web(heroku_timestamp)
        # Allow metric value to be within 10ms of 20ms to account for
        # time.sleep() inaccuracy and the time it takes to run the test.
        assert metric.value == approx(20, abs=10)

    def test_render_metrics(self):
        # Render timestamp is in integer nanoseconds
        render_timestamp = str(time.time_ns())
        time.sleep(0.02)
        metric = Metric.for_web(render_timestamp)
        # Allow metric value to be within 10ms of 20ms to account for
        # time.sleep() inaccuracy and the time it takes to run the test.
        assert metric.value == approx(20, abs=10)

    def test_nginx_metrics(self):
        # Nginx timestamp is in seconds with millisecond resolution (3dp).
        #
        # NOTE: We manually format to 3dp here because time.time() returns the
        # time in seconds with microsecond resolution (6dp).
        nginx_timestamp = f"t={time.time():.3f}"
        time.sleep(0.02)
        metric = Metric.for_web(nginx_timestamp)
        # Allow metric value to be within 10ms of 20ms to account for
        # time.sleep() inaccuracy and the time it takes to run the test.
        assert metric.value == approx(20, abs=10)

    def test_negative_value(self):
        assert Metric.for_web("t=-123456789") is None

    def test_garbage_value(self):
        assert Metric.for_web("t=abc") is None
