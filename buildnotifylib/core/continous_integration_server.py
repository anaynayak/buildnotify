from buildnotifylib.core.model import Project


class ContinuousIntegrationServer:
    def __init__(self, url: str, projects: list[Project], unavailable=False):
        self.url = url
        self.projects = projects
        self.unavailable = unavailable

    def get_projects(self) -> list[Project]:
        return self.projects
