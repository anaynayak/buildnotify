from buildnotifylib.core.project import Project
from buildnotifylib.config import Config


class ProjectBuilder:
    def __init__(self, attrs, url='someurl', prefix=None):
        self.attrs = attrs
        self.url = url
        self._prefix = prefix
        self._timezone = Config.NONE_TIMEZONE

    def server(self, url):
        self.url = url
        return self

    def prefix(self, prefix):
        self._prefix = prefix
        return self

    def timezone(self, timezone):
        self._timezone = timezone
        return self

    def build(self):
        return Project(self.url, self._prefix, self._timezone, Attrs(self.attrs))


class Attrs(dict):
    def __missing__(self, key):
        return key
