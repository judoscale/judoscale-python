import time
import unittest

from app import create_app

from judoscale.core.config import config, RuntimeContainer
from judoscale.core.reporter import reporter
from judoscale.core.utilization_tracker import utilization_tracker

# Share a single client, since each client instantiates its own middleware, it'd
# cause us to build a new web collector and register a new adapter for every client.
app = create_app()
app.config["TESTING"] = True
app.config["DEBUG"] = False
client = app.test_client()


class BasicTests(unittest.TestCase):
    def setUp(self):
        config["RUNTIME_CONTAINER"] = RuntimeContainer("web.1")

    def tearDown(self):
        # flush metrics to avoid them leaking to other tests
        reporter.all_metrics
        reporter.stop()
        utilization_tracker.stop()

    def test_index_view(self):
        response = client.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_app_logging(self):
        with self.assertLogs("DemoFlaskApp") as captured:
            response = client.get("/", follow_redirects=True)

        # assert there is only one log message
        self.assertEqual(len(captured.records), 1)
        # assert the content log message
        msg_log = captured.records[0].getMessage()
        self.assertEqual(msg_log, "Hello, world")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Judoscale Flask Sample App", response.data)

    def test_reporter_starts_even_without_the_extra_request_start_header(self):
        response = client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(reporter.is_running, True)

        # no queue time metrics gathered, only app time & utilization
        metrics = reporter.all_metrics
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0].measurement, "up")
        self.assertEqual(metrics[1].measurement, "at")

    def test_reporter_captures_metrics(self):
        now = time.time()

        response = client.get(
            "/",
            headers={
                "X-Request-Start": f"{round(now * 1000)}",
                "X-Request-Id": "00000000-0000-0000-0000-000000000000",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(reporter.is_running, True)
        self.assertEqual(utilization_tracker.is_started, True)

        # metrics are popped off the back of the queue, so the order here is reversed
        metrics = reporter.all_metrics
        self.assertEqual(len(metrics), 3)
        self.assertEqual(metrics[0].measurement, "up")
        self.assertGreater(metrics[0].value, 0)
        self.assertGreater(metrics[0].timestamp, now)
        self.assertEqual(metrics[1].measurement, "at")
        self.assertGreaterEqual(metrics[1].value, 0)
        self.assertGreater(metrics[1].timestamp, now)
        self.assertEqual(metrics[2].measurement, "qt")
        self.assertGreaterEqual(metrics[2].value, 0)
        self.assertGreater(metrics[2].timestamp, now)


if __name__ == "__main__":
    unittest.main()
