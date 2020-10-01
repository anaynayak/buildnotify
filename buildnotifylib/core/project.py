from datetime import datetime
from typing import Dict

import pytz
from dateutil.parser import parse
from dateutil.tz import tzlocal

from buildnotifylib.config import Config
from buildnotifylib.serverconfig import ServerConfig


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
        self.last_build_label = props.get('lastBuildLabel', None)

    def get_build_status(self) -> str:
        return self.status + "." + self.activity

    def label(self) -> str:
        if self.prefix:
            return "[" + self.prefix + "] " + self.name
        return self.name

    def different_builds(self, project: 'Project') -> bool:
        return self.last_build_label != project.last_build_label

    def matches(self, other: 'Project') -> bool:
        return other.name == self.name and other.server_url == self.server_url

    def get_last_build_time(self) -> datetime:
        if not self.last_build_time:
            return datetime.now(tzlocal())
        if self.timezone == Config.NONE_TIMEZONE:
            date = parse(self.last_build_time)
            if date.tzinfo is None:
                return date.replace(tzinfo=tzlocal())
            return date
        return parse(self.last_build_time).replace(tzinfo=pytz.timezone(self.timezone))
