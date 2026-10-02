from typing import Protocol

from buildnotifylib.core.model import Project
from buildnotifylib.core.settings import ServerSettings


class CertificateError(Exception):
    """Raised by a Connection when the server's TLS certificate can't be verified."""


class FetchError(Exception):
    """Raised by a Connection when a fetch fails, with a short message free of URLs and credentials."""


class Connection(Protocol):
    def connect(
        self, server: ServerSettings, timeout: float | None, additional_headers: dict[str, str] | None = None
    ) -> bytes: ...


class Source(Protocol):
    """One configured server: fetches its projects, raising on any failure."""

    def fetch(self) -> list[Project]: ...


class CredentialStore(Protocol):
    def is_available(self) -> bool: ...

    def save(self, url: str, username: str, password: str) -> None: ...

    def load(self, url: str, username: str) -> str | None: ...

    def delete(self, url: str, username: str) -> None: ...


class Hook(Protocol):
    def run(self, script: str, status: str, projects: str) -> None: ...
