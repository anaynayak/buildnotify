import requests
from requests.exceptions import SSLError

from buildnotifylib.core.settings import ServerSettings
from buildnotifylib.version import VERSION


class HttpConnection:
    def __init__(self):
        self.user_agent = f"BuildNotify/{VERSION}"
        self.session = requests.Session()

    def connect(
        self, server: ServerSettings, timeout: float | None, additional_headers: dict[str, str] | None = None
    ) -> bytes:
        headers = {"user-agent": self.user_agent}
        headers.update(additional_headers or {})

        auth = (server.username, server.password) if self.uses_basic_auth(server) else None
        response = self.session.get(
            server.url, verify=not server.skip_ssl_verification, headers=headers, auth=auth, timeout=timeout
        )
        response.raise_for_status()
        return response.content

    @staticmethod
    def uses_basic_auth(server: ServerSettings) -> bool:
        return server.authentication_type == ServerSettings.AUTH_USERNAME_PASSWORD and server.has_creds()


def is_ssl_error(error: Exception | None) -> bool:
    return isinstance(error, SSLError)
