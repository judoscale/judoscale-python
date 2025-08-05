import time
import unittest

from app import create_app

from judoscale.core.config import config, RuntimeContainer
from judoscale.core.metric import Metric
from judoscale.core.reporter import reporter


class BasicTests(unittest.TestCase):
    def setUp(self):
        config["RUNTIME_CONTAINER"] = RuntimeContainer("web.1")
        app = create_app()
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        self.client = app.test_client()

    def tearDown(self):
        # flush metrics to avoid them leaking to other tests
        reporter.all_metrics
        reporter.stop()

    def test_index_view(self):
        response = self.client.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_app_logging(self):
        with self.assertLogs("DemoFlaskApp") as captured:
            response = self.client.get("/", follow_redirects=True)

        # assert there is only one log message
        self.assertEqual(len(captured.records), 1)
        # assert the content log message
        msg_log = captured.records[0].getMessage()
        self.assertEqual(msg_log, "Hello, world")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Judoscale Flask Sample App", response.data)

    def test_reporter_starts_even_without_the_extra_request_start_header(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(reporter.is_running, True)

        # no queue time metrics gathered, only app time
        metrics = reporter.all_metrics
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0].measurement, "at")

    def test_reporter_captures_metrics(self):
        now = time.time()

        self.client.environ_base["HTTP_X_REQUEST_START"] = round(now * 1000)
        self.client.environ_base["HTTP_X_REQUEST_ID"] = "00000000-0000-0000-0000-000000000000"

        response = self.client.get("/", headers={})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(reporter.is_running, True)

        metrics = reporter.all_metrics
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0].measurement, "at")
        self.assertIsInstance(metrics[0].value, int)
        self.assertGreater(metrics[0].timestamp, now)
        self.assertEqual(metrics[1].measurement, "qt")
        self.assertIsInstance(metrics[1].value, int)
        self.assertGreater(metrics[1].timestamp, now)


if __name__ == "__main__":
    unittest.main()
