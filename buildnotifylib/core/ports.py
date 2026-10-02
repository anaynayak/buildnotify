from typing import Protocol

from buildnotifylib.core.settings import ServerSettings


class Connection(Protocol):
    def connect(
        self, server: ServerSettings, timeout: float | None, additional_headers: dict[str, str] | None = None
    ) -> bytes: ...
