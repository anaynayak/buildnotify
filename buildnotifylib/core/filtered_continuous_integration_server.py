class FilteredContinuousIntegrationServer(object):
    def __init__(self, server, filter_projects):
        self.server = server
        self.filter_projects = filter_projects
        self.unavailable = server.unavailable
        self.url = server.url

    def get_projects(self):
        return [project for project in self.server.get_projects() if project.name not in self.filter_projects]
