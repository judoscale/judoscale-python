from unittest import TestCase
from django.test import Client

from judoscale.core.reporter import reporter


class TestLogging(TestCase):
    def setUp(self):
        self.client = Client()

    def test_app_logging(self):
        with self.assertLogs() as captured:
            response = self.client.get('/')

        # assert there is only one log message
        self.assertEqual(len(captured.records), 1)
        # assert the content log message
        msg_log = captured.records[0].getMessage()
        self.assertEqual(msg_log, "Hello, world")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"Judoscale Sample App", response.content)

    def test_reporter_starts_for_each_process(self):
        with self.assertLogs() as captured:
            response = self.client.get('/')

            self.assertEqual(response.status_code, 200)
            # TODO patch the request header to return HTTP_X_REQUEST_START for test client
            self.assertEqual(reporter.is_running, True)
            print("METRICS", reporter.get_metrics())
            self.assertEqual(len(reporter.get_metrics()), 0)
