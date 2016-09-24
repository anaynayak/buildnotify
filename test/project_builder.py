from buildnotifylib.core.project import Project


class ProjectBuilder:
    def __init__(self, attrs, url='someurl', prefix=None):
        self.attrs = attrs
        self.url = url
        self._prefix = prefix

    def server(self, url):
        self.url = url
        return self

    def prefix(self, prefix):
        self._prefix = prefix
        return self

    def build(self):
        return Project(self.url, self._prefix, Attrs(self.attrs))


class Attrs(dict):
    def __missing__(self, key):
        return key
