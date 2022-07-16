from unittest import TestCase
from django.test import Client


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
