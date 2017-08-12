from PyQt5 import QtCore
from PyQt5.QtCore import QThread
from xml.dom import minidom

from buildnotifylib.core.server import ContinuousIntegrationServer, FilteredContinuousIntegrationServer
from buildnotifylib.core.project import Project
from http_connection import HttpConnection
from timed_event import BackgroundEvent
from response import Response

class OverallIntegrationStatus:
    def __init__(self, servers):
        self.servers = servers

    def get_build_status(self):
        build_status_mapping = self.to_map()
        seq = ['Failure.Building', 'Failure.Sleeping', 'Success.Building', 'Success.Sleeping', 'Failure.CheckingModifications', 'Success.CheckingModifications']
        for status in seq:
            if len(build_status_mapping[status]) > 0:
                return status
        return None

    def get_failing_builds(self):
        return filter(lambda p: p.status == 'Failure', self.get_projects())

    def to_map(self):
        status = dict(
            [('Success.Sleeping', []), ('Success.Building', []), ('Failure.CheckingModifications', []), ('Success.CheckingModifications', []), ('Failure.Sleeping', []), ('Failure.Building', []),
             ('Unknown.Building', []), ('Unknown.CheckingModifications', []), ('Unknown.Sleeping', []), ('Unknown.Unknown', [])])
        for project in self.get_projects():
            if project.get_build_status() in status:
                status[project.get_build_status()].append(project)
            else:
                status['Unknown.Unknown'].append(project)
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
    updated_projects = QtCore.pyqtSignal(object)

    def __init__(self, config, parent=None):
        QThread.__init__(self, parent)
        self.config = config
        self.listeners = []

    def load_from_server(self):
        self.start()

    def reload(self):
        BackgroundEvent(self.process, self).run()

    def process(self):
        overall_status = []
        for server_config in self.config.get_server_configs():
            overall_status.append(self.check_nodes(server_config))
        self.updated_projects.emit(OverallIntegrationStatus(overall_status))

    def run(self):
        self.process()

    def check_nodes(self, server_config):
        response = ProjectLoader(server_config, self.config.timeout).get_data()
        return FilteredContinuousIntegrationServer(response.server, server_config.excluded_projects)


class ProjectLoader:
    def __init__(self, server_config, timeout, connection=HttpConnection()):
        self.server_config = server_config
        self.timeout = timeout
        self.connection = connection

    def get_data(self):
        print "checking %s" % self.server_config.url
        try:
            data = self.connection.connect(self.server_config, self.timeout)
        except Exception, e:
            print e
            return Response(ContinuousIntegrationServer(self.server_config.url, [], True), e)
        dom = minidom.parse(data)
        print "processed %s" % self.server_config.url
        projects = []
        for node in dom.getElementsByTagName('Project'):
            projects.append(Project(
                self.server_config.url,
                self.server_config.prefix,
                self.server_config.timezone,
                {
                    'name': node.getAttribute('name'), 'lastBuildStatus': node.getAttribute('lastBuildStatus'),
                    'lastBuildLabel': node.getAttribute('lastBuildLabel'), 'activity': node.getAttribute('activity'),
                    'url': node.getAttribute('webUrl'), 'lastBuildTime': node.getAttribute('lastBuildTime')
                }))
        return Response(ContinuousIntegrationServer(self.server_config.url, projects))
