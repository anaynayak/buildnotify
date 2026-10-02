from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from urllib.parse import urlparse

NONE_TIMEZONE = "None"
VALID_SCHEMES = ("http", "https", "file")


class Status(StrEnum):
    """cctray lastBuildStatus, declared from highest to lowest priority."""

    FAILURE = "Failure"
    SUCCESS = "Success"
    UNKNOWN = "Unknown"

    @classmethod
    def parse(cls, value: str) -> "Status":
        try:
            return cls("Failure" if value == "Exception" else value)
        except ValueError:
            return cls.UNKNOWN

    @property
    def priority(self) -> int:
        return list(Status).index(self)


class Activity(StrEnum):
    """cctray activity, declared from highest to lowest priority."""

    BUILDING = "Building"
    SLEEPING = "Sleeping"
    CHECKING_MODIFICATIONS = "CheckingModifications"
    UNKNOWN = "Unknown"

    @classmethod
    def parse(cls, value: str) -> "Activity":
        try:
            return cls(value)
        except ValueError:
            return cls.UNKNOWN

    @property
    def priority(self) -> int:
        return list(Activity).index(self)


def normalise_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in VALID_SCHEMES:
        return "http://" + url
    return parsed.geturl()


@dataclass(frozen=True)
class Project:
    server_url: str
    name: str
    status: Status
    activity: Activity
    url: str
    last_build_time: str = ""
    build_time: datetime | None = None
    last_build_label: str | None = None
    prefix: str | None = None

    def get_build_status(self) -> str:
        return f"{self.status}.{self.activity}"

    def label(self, show_last_build_label: bool = False) -> str:
        label = f"[{self.prefix}] {self.name}" if self.prefix else self.name
        if show_last_build_label:
            label = f"{label} ({self.last_build_label})"
        return label

    def different_builds(self, project: "Project") -> bool:
        return (self.last_build_label, self.last_build_time) != (project.last_build_label, project.last_build_time)


@dataclass(frozen=True)
class ServerSnapshot:
    url: str
    projects: tuple[Project, ...] = ()
    error: Exception | None = field(default=None, compare=False)
    error_at: datetime | None = field(default=None, compare=False)

    def __post_init__(self) -> None:
        if self.error is not None and self.error_at is None:
            object.__setattr__(self, "error_at", datetime.now(UTC))

    @property
    def unavailable(self) -> bool:
        return self.error is not None
