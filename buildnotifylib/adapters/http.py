import socket
import threading
from urllib.parse import urlsplit

import requests
from requests.exceptions import HTTPError, RequestException, SSLError, Timeout
from urllib3.exceptions import NameResolutionError

from buildnotifylib.core.ports import (
    CannotConnect,
    CertificateError,
    FetchError,
    FetchTimeout,
    HostNotFound,
    Response,
)
from buildnotifylib.core.settings import ServerSettings
from buildnotifylib.version import VERSION


class HttpConnection:
    def __init__(self) -> None:
        self.user_agent = f"BuildNotify/{VERSION}"
        self.local = threading.local()

    @property
    def session(self) -> requests.Session:
        """One Session per thread: the poller fetches servers in parallel and Session is not thread-safe."""
        session: requests.Session | None = getattr(self.local, "session", None)
        if session is None:
            session = self.local.session = requests.Session()
        return session

    def connect(
        self, server: ServerSettings, timeout: float | None, additional_headers: dict[str, str] | None = None
    ) -> bytes:
        headers = {"user-agent": self.user_agent}
        headers.update(additional_headers or {})

        auth = (server.username, server.password) if self.uses_basic_auth(server) else None
        try:
            response = self.session.get(
                server.url, verify=not server.skip_ssl_verification, headers=headers, auth=auth, timeout=timeout
            )
            response.raise_for_status()
        except SSLError as ex:
            raise CertificateError(str(ex)) from ex
        except RequestException as ex:
            raise self.describe(ex, server.url) from ex
        return response.content

    def request(self, url: str, timeout: float | None, headers: dict[str, str], verify: bool = True) -> Response:
        """GET without raising for HTTP error statuses, so the caller can read them and their headers."""
        try:
            response = self.session.get(
                url, verify=verify, headers={"user-agent": self.user_agent, **headers}, timeout=timeout
            )
        except SSLError as ex:
            raise CertificateError(str(ex)) from ex
        except RequestException as ex:
            raise self.describe(ex, url) from ex
        lowered = {name.lower(): value for name, value in response.headers.items()}
        return Response(response.status_code, lowered, response.content)

    @staticmethod
    def describe(error: RequestException, url: str) -> FetchError:
        if isinstance(error, HTTPError) and error.response is not None:
            status = error.response.status_code
            return FetchError(f"HTTP {status} {error.response.reason or ''}".strip(), status)
        if isinstance(error, Timeout):
            return FetchTimeout("Timed out")
        if isinstance(error, requests.ConnectionError):
            kind = HostNotFound if unresolved(error) else CannotConnect
            return kind(f"Could not connect to {urlsplit(url).hostname}")
        return FetchError(f"Request failed ({type(error).__name__})")

    @staticmethod
    def uses_basic_auth(server: ServerSettings) -> bool:
        return server.authentication_type == ServerSettings.AUTH_USERNAME_PASSWORD and server.has_creds()


def unresolved(error: requests.ConnectionError) -> bool:
    """requests wraps urllib3's MaxRetryError, whose reason is the error that ended the last attempt."""
    cause = error.args[0] if error.args else None
    return isinstance(getattr(cause, "reason", cause), NameResolutionError | socket.gaierror)
