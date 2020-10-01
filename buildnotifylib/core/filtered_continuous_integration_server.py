from typing import List

from buildnotifylib.core.project import Project

from buildnotifylib.core.continous_integration_server import ContinuousIntegrationServer


class FilteredContinuousIntegrationServer(object):
    def __init__(self, server: ContinuousIntegrationServer, filter_projects: List[str]):
        self.server = server
        self.filter_projects = filter_projects
        self.unavailable = server.unavailable
        self.url = server.url

    def get_projects(self) -> List[Project]:
        return [project for project in self.server.get_projects() if project.name not in self.filter_projects]
