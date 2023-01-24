import datetime
from unittest import TestCase

from django.test import Client

from judoscale.core.metrics_collectors import WebMetricsCollector
from judoscale.core.reporter import reporter


class TestApp(TestCase):
    def setUp(self):
        self.client = Client()
        reporter.add_collector(WebMetricsCollector())

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

        # no metrics gathered
        self.assertEqual(len(reporter.all_metrics), 0)

    def test_reporter_captures_metrics(self):
        now = datetime.datetime.now().timestamp()

        response = self.client.get(
            "/",
            HTTP_X_REQUEST_START=f"{now}",
            HTTP_X_REQUEST_ID="00000000-0000-0000-0000-000000000000",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(reporter.is_running, True)

        metrics = reporter.all_metrics
        print("METRIC", metrics)
        self.assertEqual(len(metrics), 1)
        self.assertNotEqual(metrics[0].value, None)
        self.assertNotEqual(metrics[0].timestamp, None)
