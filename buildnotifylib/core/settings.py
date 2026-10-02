from dataclasses import dataclass, field
from typing import ClassVar

from buildnotifylib.core.model import NONE_TIMEZONE, normalise_url


@dataclass
class ServerSettings:
    AUTH_USERNAME_PASSWORD: ClassVar[int] = 0
    AUTH_BEARER_TOKEN: ClassVar[int] = 1

    url: str
    excluded_projects: list[str] = field(default_factory=list)
    timezone: str = NONE_TIMEZONE
    prefix: str = ""
    username: str = ""
    password: str = ""
    skip_ssl_verification: bool = False
    authentication_type: int = AUTH_USERNAME_PASSWORD

    def __post_init__(self):
        self.url = normalise_url(self.url)

    def has_creds(self) -> bool:
        return bool(self.username)

    def uses_keyring(self) -> bool:
        return self.has_creds() or self.authentication_type == self.AUTH_BEARER_TOKEN
