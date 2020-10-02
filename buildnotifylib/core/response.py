from buildnotifylib.core.continous_integration_server import ContinuousIntegrationServer
from requests.exceptions import SSLError


class Response(object):
    def __init__(self, server: ContinuousIntegrationServer, error: Exception = None):
        self.server = server
        self.error = error

    def failed(self) -> bool:
        return self.error is not None

    def ssl_error(self) -> bool:
        try:
            return self.failed() and type(self.error) is SSLError
        except AttributeError:
            return False
