import unittest
from buildnotifylib.core.response import Response
from requests.exceptions import SSLError

class ResponseTest(unittest.TestCase):
    def test_should_return_ssl_error(self):
        response = Response({}, SSLError())

        self.assertTrue(response.failed())
        self.assertTrue(response.ssl_error())
