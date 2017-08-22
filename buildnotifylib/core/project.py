from datetime import datetime
from urlparse import urlparse

import pytz
from dateutil.parser import parse
from dateutil.tz import tzlocal

from buildnotifylib.config import Config


class Project(object):
    def __init__(self, server_url, prefix, timezone, props):
        self.server_url = server_url
        self.prefix = prefix
        self.timezone = timezone
        self.name = props['name']
        self.status = props['lastBuildStatus']
        self.activity = props['activity']
        self.url = urlparse(props['url'], 'http').geturl().replace('///', '//')
        self.last_build_time = props['lastBuildTime']
        self.last_build_label = props.get('lastBuildLabel', None)

    def get_build_status(self):
        return self.status + "." + self.activity

    def label(self):
        if self.prefix:
            return "[" + self.prefix + "] " + self.name
        return self.name

    def different_builds(self, project):
        return self.last_build_label != project.last_build_label

    def matches(self, other):
        return other.name == self.name and other.server_url == self.server_url

    def get_last_build_time(self):
        if not self.last_build_time:
            return datetime.now(tzlocal())
        if self.timezone == Config.NONE_TIMEZONE:
            date = parse(self.last_build_time)
            if date.tzinfo is None:
                return date.replace(tzinfo=tzlocal())
            return date
        return parse(self.last_build_time).replace(tzinfo=pytz.timezone(self.timezone))
