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
    def __init__(self, url, projects):
        self.url = url
        self.projects = projects

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
            if server.projects is not None:
                all_projects.extend(server.projects)
        return all_projects

    def unavailable_servers(self):
        return filter(lambda server: server.projects is None, self.servers)

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
        print "checking %s" % url
        try:
            data = HttpConnection().connect(url, self.config.timeout)
        except (Exception), e:
            print e
            return ContinuousIntegrationServer(url, None)
        dom = minidom.parse(data)
        print "processed %s" % url
        projects = []
        for node in dom.getElementsByTagName('Project'):
            projects.append(Project({'name': node.getAttribute('name'), 'lastBuildStatus':node.getAttribute('lastBuildStatus'),
                                     'activity': node.getAttribute('activity'), 'url': node.getAttribute('webUrl'), 'lastBuildTime': node.getAttribute('lastBuildTime')}))
        return ContinuousIntegrationServer(url, projects)

