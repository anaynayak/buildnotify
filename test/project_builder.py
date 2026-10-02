from dataclasses import dataclass, field

from buildnotifylib.core import cctray
from buildnotifylib.core.model import NONE_TIMEZONE, Project


@dataclass
class Source:
    url: str
    prefix: str | None
    timezone: str
    excluded_projects: list[str] = field(default_factory=list)


class ProjectBuilder:
    def __init__(self, attrs, url="someurl", prefix=None):
        self.attrs = attrs
        self.url = url
        self._prefix = prefix
        self._timezone = NONE_TIMEZONE

    def server(self, url):
        self.url = url
        return self

    def prefix(self, prefix):
        self._prefix = prefix
        return self

    def timezone(self, timezone):
        self._timezone = timezone
        return self

    def build(self) -> Project:
        attrs = Attrs(self.attrs)
        attrs.setdefault("webUrl", attrs["url"])
        return cctray.to_project(attrs, Source(self.url, self._prefix, self._timezone))


class Attrs(dict):
    def __missing__(self, key):
        return key
