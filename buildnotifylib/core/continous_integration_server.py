class ContinuousIntegrationServer(object):
    def __init__(self, url, projects, unavailable=False):
        self.url = url
        self.projects = projects
        self.unavailable = unavailable

    def get_projects(self):
        return self.projects
