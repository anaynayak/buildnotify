from datetime import datetime, tzinfo
from typing import Dict, Optional
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from buildnotifylib.config import Config
from buildnotifylib.serverconfig import ServerConfig

FAILURE_STATUSES = ('Failure', 'Exception')


class Project(object):
    def __init__(self, server_url: str, prefix: str, timezone: str, props: Dict[str, str]):
        self.server_url = server_url
        self.prefix = prefix
        self.timezone = timezone
        self.name = props['name']
        self.status = props['lastBuildStatus']
        self.activity = props['activity']
        self.url = ServerConfig.cleanup(props['url'])
        self.last_build_time = props['lastBuildTime']
        self.build_time = parse_build_time(self.last_build_time, timezone)
        self.last_build_label = props.get('lastBuildLabel', None)

    def effective_status(self) -> str:
        return 'Failure' if self.status in FAILURE_STATUSES else self.status

    def get_build_status(self) -> str:
        return self.effective_status() + "." + self.activity

    def label(self, show_last_build_label: bool = False) -> str:
        label = self.name

        if self.prefix:
            label = '[%s] %s' % (self.prefix, self.name)
        if show_last_build_label:
            label = '%s (%s)' % (label, self.last_build_label)

        return label

    def different_builds(self, project: 'Project') -> bool:
        return self.last_build_label != project.last_build_label

    def matches(self, other: 'Project') -> bool:
        return other.name == self.name and other.server_url == self.server_url

    def get_last_build_time(self) -> Optional[datetime]:
        return self.build_time


def server_zone(timezone: str) -> Optional[tzinfo]:
    if timezone == Config.NONE_TIMEZONE:
        return None
    try:
        return ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, ValueError):
        return None


def parse_build_time(value: str, timezone: str) -> Optional[datetime]:
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
