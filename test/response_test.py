import unittest
from buildnotifylib.core.response import Response
from requests.exceptions import SSLError


class ResponseTest(unittest.TestCase):
    def test_should_return_ssl_error(self):
        response = Response({}, SSLError())

        self.assertTrue(response.failed())
        self.assertTrue(response.ssl_error())

    def test_should_return_ssl_error_for_subclass(self):
        class CertificateError(SSLError):
            pass

        self.assertTrue(Response({}, CertificateError()).ssl_error())

    def test_should_not_return_ssl_error_for_other_errors(self):
        self.assertFalse(Response({}, ValueError()).ssl_error())
