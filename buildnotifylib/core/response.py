from buildnotifylib.core.continous_integration_server import ContinuousIntegrationServer
from requests.exceptions import SSLError


class Response(object):
    def __init__(self, server: ContinuousIntegrationServer, error: Exception = None):
        self.server = server
        self.error = error

    def failed(self) -> bool:
        return self.error is not None

    def ssl_error(self) -> bool:
        return isinstance(self.error, SSLError)
