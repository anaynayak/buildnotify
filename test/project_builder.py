from buildnotifylib.core.project import Project


class ProjectBuilder:
    def __init__(self, attrs):
        self.attrs = attrs

    def build(self):
        return Project(Attrs(self.attrs))


class Attrs(dict):
    def __missing__(self, key):
        return key
