from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import ClassVar

from buildnotifylib.core.model import NONE_TIMEZONE, normalise_url

GITHUB_URL = "https://github.com/"


class SourceKind(StrEnum):
    CCTRAY = "cctray"
    GITHUB = "github"

    @classmethod
    def parse(cls, value: str) -> "SourceKind":
        try:
            return cls(value)
        except ValueError:
            return cls.CCTRAY


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
    kind: SourceKind = SourceKind.CCTRAY
    repository: str = ""
    workflow: str = ""
    branch: str = ""
    muted: bool = False
    muted_projects: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.kind = SourceKind.parse(self.kind)
        if self.kind is SourceKind.GITHUB and self.repository:
            self.url = GITHUB_URL + self.repository
        self.url = normalise_url(self.url)

    def has_creds(self) -> bool:
        return bool(self.username)

    def uses_keyring(self) -> bool:
        return self.has_creds() or self.authentication_type == self.AUTH_BEARER_TOKEN


SCHEMA_VERSION = 5
DEFAULT_SCRIPT = ""
DEFAULT_NOTIFICATIONS = {
    "successfulBuild": False,
    "brokenBuild": True,
    "fixedBuild": True,
    "stillFailingBuild": True,
    "connectivityIssues": True,
    "lastBuildTimeForProject": True,
}


class SortKey(StrEnum):
    STATUS = "sort_status"
    LAST_BUILD_TIME = "sort_build_time"
    NAME = "sort_name"


@dataclass
class AppSettings:
    servers: list[ServerSettings] = field(default_factory=list)
    interval_seconds: int = 120
    timeout_seconds: int = 10
    custom_script: str = DEFAULT_SCRIPT
    custom_script_enabled: bool = False
    sort_key: SortKey = SortKey.STATUS
    show_last_build_label: bool = False
    symbolic_icons: bool = False
    server_prompt_shown: bool = False
    notifications: dict[str, bool] = field(default_factory=dict)
    paused_until: datetime | None = None

    def notify(self, event: str) -> bool:
        return self.notifications.get(event, DEFAULT_NOTIFICATIONS[event])
