import time

from pytest import approx

from judoscale.core.config import Config
from judoscale.core.config import config as judoconfig
from judoscale.core.metric import Metric
from judoscale.core.platform import Unknown


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

    def test_request_over_max_size(self):
        request_start = str(round(time.time() * 1000))
        config = Config(Unknown(""), {})

        assert Metric.for_web(request_start, "100001", config=config) is None
        assert Metric.for_web(request_start, 100_001, config=config) is None

    def test_request_up_to_max_size(self):
        request_start = str(round(time.time() * 1000))
        config = Config(Unknown(""), {})

        assert Metric.for_web(request_start, None, config=config) is not None
        assert Metric.for_web(request_start, "", config=config) is not None
        assert Metric.for_web(request_start, "512", config=config) is not None
        assert Metric.for_web(request_start, 512, config=config) is not None
        assert Metric.for_web(request_start, "100000", config=config) is not None
        assert Metric.for_web(request_start, "not-a-number", config=config) is not None

    def test_no_max_request_size(self):
        request_start = str(round(time.time() * 1000))
        config = Config(Unknown(""), {})
        config.update({"MAX_REQUEST_SIZE_BYTES": None})

        assert Metric.for_web(request_start, "10000000", config=config) is not None

    def test_max_request_size_from_judoscale_config(self, monkeypatch):
        request_start = str(round(time.time() * 1000))
        monkeypatch.setitem(judoconfig, "MAX_REQUEST_SIZE_BYTES", 1_000)

        assert Metric.for_web(request_start, "1000") is not None
        assert Metric.for_web(request_start, "1001") is None


class TestMetricsForQueueDepth:
    def test_for_queue_depth(self):
        queue_name = "default"
        depth = 3
        before = round(time.time())
        metric = Metric.for_queue_depth(queue_name, depth)
        after = round(time.time())

        ts, value, measurement, name = metric.as_tuple
        assert before <= ts <= after
        assert value == depth
        assert measurement == "qd"
        assert name == queue_name
