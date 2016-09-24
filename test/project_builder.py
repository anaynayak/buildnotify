from buildnotifylib.core.project import Project


class ProjectBuilder:
    def __init__(self, attrs, url='someurl', prefix=None):
        self.attrs = attrs
        self.url = url
        self.prefix = prefix

    def server(self, url):
        self.url = url
        return self

    def prefix(self, prefix):
        self.prefix = prefix
        return self

    def build(self):
        return Project(self.url, self.prefix, Attrs(self.attrs))


class Attrs(dict):
    def __missing__(self, key):
        return key
