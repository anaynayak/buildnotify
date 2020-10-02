from typing import List

from buildnotifylib.core.project import Project


class ContinuousIntegrationServer(object):
    def __init__(self, url: str, projects: List[Project], unavailable=False):
        self.url = url
        self.projects = projects
        self.unavailable = unavailable

    def get_projects(self) -> List[Project]:
        return self.projects
