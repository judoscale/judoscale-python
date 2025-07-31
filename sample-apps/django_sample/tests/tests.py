import datetime
from unittest import TestCase

from django.test import Client

from judoscale.core.config import config, RuntimeContainer
from judoscale.core.reporter import reporter
from judoscale.core.utilization_tracker import utilization_tracker


class TestApp(TestCase):
    def setUp(self):
        config["RUNTIME_CONTAINER"] = RuntimeContainer("web.1")
        self.client = Client()

    def tearDown(self):
        # flush metrics to avoid them leaking to other tests
        reporter.all_metrics
        reporter.stop()
        utilization_tracker.stop()

    def test_index_view(self):
        response = self.client.get("/", follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_app_logging(self):
        with self.assertLogs() as captured:
            response = self.client.get("/")

        # assert there is only one log message
        self.assertEqual(len(captured.records), 1)
        # assert the content log message
        msg_log = captured.records[0].getMessage()
        self.assertEqual(msg_log, "Hello, world")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Judoscale Django Sample App", response.content)

    def test_reporter_starts_even_without_the_extra_request_start_header(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(reporter.is_running, True)

        # no queue time metrics gathered, only app time
        metrics = reporter.all_metrics
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0].measurement, "at")

    def test_reporter_captures_metrics(self):
        now = datetime.datetime.now().timestamp()

        response = self.client.get(
            "/",
            HTTP_X_REQUEST_START=f"{now}",
            HTTP_X_REQUEST_ID="00000000-0000-0000-0000-000000000000",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(reporter.is_running, True)

        # metrics are popped off the back of the queue, so the order here is reversed
        metrics = reporter.all_metrics
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0].measurement, "at")
        self.assertIsInstance(metrics[0].value, int)
        self.assertGreater(metrics[0].timestamp, now)
        self.assertEqual(metrics[1].measurement, "qt")
        self.assertIsInstance(metrics[1].value, int)
        self.assertGreater(metrics[1].timestamp, now)

    def test_utilization_tracking(self):
        response = self.client.get("/test_utilization_tracker")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(utilization_tracker.is_running, True)
        self.assertEqual(response.content, b"utilization_tracker=1")

        # State was tracked once mid-request, and now after it's finished.
        utilization_tracker._track_current_state()

        # metrics are popped off the back of the queue, so the order here is reversed
        metrics = reporter.all_metrics
        self.assertEqual(len(metrics), 5)
        self.assertEqual(metrics[0].measurement, "ru")
        self.assertEqual(metrics[0].value, 0)
        self.assertEqual(metrics[1].measurement, "pu")
        self.assertEqual(metrics[1].value, 0)
        self.assertEqual(metrics[2].measurement, "at")
        self.assertEqual(metrics[3].measurement, "ru")
        self.assertEqual(metrics[3].value, 1)
        self.assertEqual(metrics[4].measurement, "pu")
        self.assertEqual(metrics[4].value, 1)
