import socket
import urllib2
from xml.dom import minidom

from dateutil.parser import parse

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

class ProjectsPopulator:    
    def __init__(self, config):
        self.config = config
        self.listeners = []

    def add_listener(self, listener):
        self.listeners.append(listener)
    
    def load_from_server(self, conf):
        overall_status = [];
        for url in self.config.get_urls():
            overall_status.append(self.check_nodes(conf, str(url)))
        self.notify_listeners(OverallIntegrationStatus(overall_status))
    
    def notify_listeners(self, integration_status):
        for listener in self.listeners:
            listener.update_projects(integration_status)

    def check_nodes(self, conf, url):
        socket.setdefaulttimeout(conf.timeout)
        try:
            data = urllib2.urlopen(url)
        except (Exception), e:
            print e
            return ContinuousIntegrationServer(url, None)
        dom = minidom.parse(data)
        projects = []
        for node in dom.getElementsByTagName('Project'):
            projects.append(Project({'name': node.getAttribute('name'), 'lastBuildStatus':node.getAttribute('lastBuildStatus'),
                                     'activity': node.getAttribute('activity'), 'url': node.getAttribute('webUrl'), 'lastBuildTime': node.getAttribute('lastBuildTime')}))
        return ContinuousIntegrationServer(url, projects)
