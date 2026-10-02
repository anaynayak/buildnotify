from typing import Protocol

from buildnotifylib.core.settings import ServerSettings


class Connection(Protocol):
    def connect(
        self, server: ServerSettings, timeout: float | None, additional_headers: dict[str, str] | None = None
    ) -> bytes: ...


class CredentialStore(Protocol):
    def save(self, url: str, username: str, password: str) -> None: ...

    def load(self, url: str, username: str) -> str | None: ...

    def delete(self, url: str, username: str) -> None: ...
