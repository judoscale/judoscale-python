import time
import unittest
from typing import List

from app import create_app

from judoscale.core.metric import Metric
from judoscale.core.reporter import reporter


class BasicTests(unittest.TestCase):
    def setUp(self):
        """Setup executed prior to each test"""
        app = create_app()
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        self.client = app.test_client()

    def tearDown(self):
        """Teardown executed after each test"""
        pass

    def test_index_view(self):
        response = self.client.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_app_logging(self):
        with self.assertLogs() as captured:
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

        # no metrics gathered
        self.assertEqual(len(reporter.all_metrics), 0)

    def test_reporter_captures_metrics(self):
        now = round(time.time() * 1000)
        self.client.environ_base["HTTP_X_REQUEST_START"] = now
        self.client.environ_base[
            "HTTP_X_REQUEST_ID"
        ] = "00000000-0000-0000-0000-000000000000"

        response = self.client.get("/", headers={})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(reporter.is_running, True)

        metrics: List[Metric] = reporter.all_metrics
        self.assertEqual(len(metrics), 1)
        self.assertNotEqual(metrics[0].value, None)
        self.assertNotEqual(metrics[0].timestamp, None)


if __name__ == "__main__":
    unittest.main()
