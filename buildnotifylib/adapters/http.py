import threading
from urllib.parse import urlsplit

import requests
from requests.exceptions import HTTPError, RequestException, SSLError, Timeout

from buildnotifylib.core.ports import CertificateError, FetchError, Response
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
            raise FetchError(self.describe(ex, server.url)) from ex
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
            raise FetchError(self.describe(ex, url)) from ex
        lowered = {name.lower(): value for name, value in response.headers.items()}
        return Response(response.status_code, lowered, response.content)

    @staticmethod
    def describe(error: RequestException, url: str) -> str:
        if isinstance(error, HTTPError) and error.response is not None:
            return f"HTTP {error.response.status_code} {error.response.reason or ''}".strip()
        if isinstance(error, Timeout):
            return "Timed out"
        if isinstance(error, requests.ConnectionError):
            return f"Could not connect to {urlsplit(url).hostname}"
        return f"Request failed ({type(error).__name__})"

    @staticmethod
    def uses_basic_auth(server: ServerSettings) -> bool:
        return server.authentication_type == ServerSettings.AUTH_USERNAME_PASSWORD and server.has_creds()
