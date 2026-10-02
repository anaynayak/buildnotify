from requests.exceptions import SSLError

from buildnotifylib.core.continous_integration_server import ContinuousIntegrationServer


class Response:
    def __init__(self, server: ContinuousIntegrationServer, error: Exception | None = None):
        self.server = server
        self.error = error

    def failed(self) -> bool:
        return self.error is not None

    def ssl_error(self) -> bool:
        return isinstance(self.error, SSLError)
