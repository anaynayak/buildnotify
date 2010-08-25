from xml.dom import minidom
from http_connection import HttpConnection
from dateutil.parser import parse
from PyQt4.QtCore import QThread
from PyQt4 import QtCore

class Project:
    def __init__(self, props):
        self.name = props['name']
        self.status = props['lastBuildStatus']
        self.activity = props['activity']
        self.lastBuildTime = parse(props['lastBuildTime']).replace(tzinfo=None)
        self.url = props['url']

    def get_build_status(self):
        return self.status + "." + self.activity

class ContinuousIntegrationServer:
    def __init__(self, url, projects, unavailable = False):
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
    
class OverallIntegrationStatus:
    def __init__(self, servers):
        self.servers = servers
        
    def get_build_status(self):
        map = self.to_map()
        seq = ['Failure.Building', 'Failure.Sleeping', 'Success.Building', 'Success.Sleeping', 'Failure.CheckingModifications', 'Success.CheckingModifications']
        for status in seq:
            if len(map[status]) > 0:
                return status
        return None
           
    def get_failing_builds(self):
        failing_builds = []
        for project in self.get_projects():
            if project.status == 'Failure':
                failing_builds.append(project)
        return failing_builds
    
    def to_map(self):
        status = dict([('Success.Sleeping', []), ('Success.Building', []),
        ('Failure.CheckingModifications', []), ('Success.CheckingModifications', []),
        ('Failure.Sleeping', []), ('Failure.Building', [])])
        for project in self.get_projects():
            status[project.get_build_status()].append(project)
        return status

    def get_projects(self):
        all_projects = []
        for server in self.servers:
            if server.get_projects() is not None:
                all_projects.extend(server.get_projects())
        return all_projects

    def unavailable_servers(self):
        return filter(lambda server: server.unavailable, self.servers)

class ProjectsPopulator(QThread):    
    def __init__(self, config, parent = None):
        QThread.__init__(self, parent)
        self.config = config
        self.listeners = []

    def load_from_server(self):
        self.start()
        
    def process(self):
        overall_status = [];
        for url in self.config.get_urls():
            overall_status.append(self.check_nodes(str(url)))
        self.emit(QtCore.SIGNAL('updated_projects'), OverallIntegrationStatus(overall_status))
    
    def run(self):
        self.process()
        
    def check_nodes(self, url):
        return FilteredContinuousIntegrationServer(ProjectLoader(url, self.config.timeout).get_data(), self.config.get_project_excludes(url));

class ProjectLoader:
    def __init__(self, url, timeout):
        self.url = url
        self.timeout = timeout
        
    def get_data(self):
        print "checking %s" % self.url
        try:
            data = HttpConnection().connect(self.url, self.timeout)
        except (Exception), e:
            print e
            return ContinuousIntegrationServer(self.url, [], True)
        dom = minidom.parse(data)
        print "processed %s" % self.url
        projects = []
        for node in dom.getElementsByTagName('Project'):
            projects.append(Project({'name': node.getAttribute('name'), 'lastBuildStatus':node.getAttribute('lastBuildStatus'),
                                     'activity': node.getAttribute('activity'), 'url': node.getAttribute('webUrl'), 'lastBuildTime': node.getAttribute('lastBuildTime')}))
        return ContinuousIntegrationServer(self.url, projects)
