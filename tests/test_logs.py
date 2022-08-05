import io
import logging
import unittest
from unittest import TestCase


class TestReporter(TestCase):
    def setUp(self):
        self.stream = io.StringIO()
        self.logger = logging.getLogger("")
        stdout_handler = logging.StreamHandler(self.stream)
        fmt = "%(levelname)s - [Judoscale] %(message)s"
        stdout_handler.setFormatter(logging.Formatter(fmt))
        self.logger.addHandler(stdout_handler)

    def tearDown(self):
        self.stream.close()
        logging.shutdown()

    def test_judo_logging(self):
        msg = 'foo'
        self.logger.warning(msg)
        msg_log = self.stream.getvalue()
        self.assertIn("[Judoscale]", msg_log)
