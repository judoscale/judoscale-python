import time
import unittest
from typing import List

from app.main import create_app
from fastapi.testclient import TestClient

from judoscale.core.config import config, RuntimeContainer
from judoscale.core.metric import Metric
from judoscale.core.reporter import reporter


class BasicTests(unittest.TestCase):
    def setUp(self):
        """Setup executed prior to each test"""
        config["RUNTIME_CONTAINER"] = RuntimeContainer("web.1")
        app = create_app()
        self.client = TestClient(app)

    def tearDown(self):
        """Teardown executed after each test"""
        pass

    def test_index_view(self):
        response = self.client.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_app_logging(self):
        with self.assertLogs('fastapi') as captured:
            response = self.client.get("/", follow_redirects=True)

        # assert there is only one log message
        self.assertEqual(len(captured.records), 1)
        # assert the content log message
        msg_log = captured.records[0].getMessage()
        self.assertEqual(msg_log, "Hello, world")
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Judoscale FastAPI Sample App", response.text)

    def test_reporter_starts_even_without_the_extra_request_start_header(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(reporter.is_running, True)

        # no metrics gathered
        self.assertEqual(len(reporter.all_metrics), 0)

    def test_reporter_captures_metrics(self):
        now = round(time.time() * 1000)

        response = self.client.get("/", headers={
          "X-Request-Start": f"{now}",
          "X-Request-Id": "00000000-0000-0000-0000-000000000000"
        })

        self.assertEqual(response.status_code, 200)
        self.assertEqual(reporter.is_running, True)

        metrics: List[Metric] = reporter.all_metrics
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0].measurement, "qt")
        self.assertNotEqual(metrics[0].value, None)
        self.assertNotEqual(metrics[0].timestamp, None)


if __name__ == "__main__":
    unittest.main()
