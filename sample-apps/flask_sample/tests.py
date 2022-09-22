import unittest

from app import app


class BasicTests(unittest.TestCase):
    def setUp(self):
        """ Setup executed prior to each test """
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        self.app = app.test_client()

    def tearDown(self):
        """ Teardown executed after each test """
        pass

    def test_main_page(self):
        response = self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

    def test_app_logging(self):
        with self.assertLogs() as captured:
            response = self.app.get('/', follow_redirects=True)

        # assert there is only one log message
        self.assertEqual(len(captured.records), 1)
        # assert the content log message
        msg_log = captured.records[0].getMessage()
        self.assertEqual(msg_log, "Hello, world")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(b"Judoscale Flask Sample App", response.data)


if __name__ == "__main__":
    unittest.main()
