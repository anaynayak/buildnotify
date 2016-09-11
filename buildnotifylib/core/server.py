class ContinuousIntegrationServer:
    def __init__(self, url, projects, unavailable=False):
        self.url = url
        self.projects = projects
        self.unavailable = unavailable

    def get_projects(self):
        return self.projects


class FilteredContinuousIntegrationServer:
    def __init__(self, server, filter_projects):
        self.server = server
        self.filter_projects = filter_projects
        self.unavailable = server.unavailable
        self.url = server.url

    def get_projects(self):
        return filter(lambda project: project.name not in self.filter_projects, self.server.get_projects())