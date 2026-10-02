from collections.abc import Mapping, Sequence
from datetime import datetime, tzinfo
from typing import Protocol
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from defusedxml import minidom

from buildnotifylib.core.model import NONE_TIMEZONE, Activity, Project, Status, normalise_url
from buildnotifylib.core.ports import Connection
from buildnotifylib.core.settings import ServerSettings

ATTRIBUTES = ("name", "lastBuildStatus", "lastBuildLabel", "activity", "webUrl", "lastBuildTime")


class FeedSource(Protocol):
    @property
    def url(self) -> str: ...

    @property
    def prefix(self) -> str | None: ...

    @property
    def timezone(self) -> str: ...

    @property
    def excluded_projects(self) -> Sequence[str]: ...


class FeedError(ValueError):
    pass


class CctraySource:
    def __init__(
        self, server: ServerSettings, timeout: float | None, connection: Connection, apply_excludes: bool = True
    ):
        self.server = server
        self.timeout = timeout
        self.connection = connection
        self.apply_excludes = apply_excludes

    def fetch(self) -> list[Project]:
        headers = {}
        if self.server.authentication_type == ServerSettings.AUTH_BEARER_TOKEN:
            headers["Authorization"] = f"Bearer {self.server.password}"
        data = self.connection.connect(self.server, self.timeout, headers)
        return parse(data, self.server, apply_excludes=self.apply_excludes)


def parse(data: bytes, server: FeedSource, *, apply_excludes: bool = True) -> list[Project]:
    projects = [to_project(attributes, server) for attributes in read_feed(data)]
    if not apply_excludes:
        return projects
    return [project for project in projects if project.name not in server.excluded_projects]


def read_feed(data: bytes) -> list[dict[str, str]]:
    try:
        dom = minidom.parseString(data)
    except Exception as ex:
        raise FeedError(str(ex)) from ex
    root = dom.documentElement.tagName
    if root != "Projects":
        raise FeedError(f"Not a cctray feed: expected <Projects> as the root element, got <{root}>")
    return [{name: node.getAttribute(name) for name in ATTRIBUTES} for node in dom.getElementsByTagName("Project")]


def to_project(attributes: Mapping[str, str], server: FeedSource) -> Project:
    return Project(
        server_url=server.url,
        name=attributes["name"],
        status=Status.parse(attributes["lastBuildStatus"]),
        activity=Activity.parse(attributes["activity"]),
        url=normalise_url(attributes["webUrl"]),
        last_build_time=attributes["lastBuildTime"],
        build_time=parse_build_time(attributes["lastBuildTime"], server.timezone),
        last_build_label=attributes.get("lastBuildLabel"),
        prefix=server.prefix,
    )


def server_zone(timezone: str) -> tzinfo | None:
    if timezone == NONE_TIMEZONE:
        return None
    try:
        return ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError):
        return None


def parse_build_time(value: str, timezone: str) -> datetime | None:
    try:
        date = datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None
    if date.tzinfo is not None:
        return date
    zone = server_zone(timezone)
    if zone is None:
        return date.astimezone()
    return date.replace(tzinfo=zone)
