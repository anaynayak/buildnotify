from typing import Optional, List, Dict
from defusedxml import minidom

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, QObject
from buildnotifylib.config import Config

from buildnotifylib.core.continous_integration_server import ContinuousIntegrationServer
from buildnotifylib.core.filtered_continuous_integration_server import FilteredContinuousIntegrationServer
from buildnotifylib.core.http_connection import HttpConnection
from buildnotifylib.core.project import Project
from buildnotifylib.core.response import Response
from buildnotifylib.serverconfig import ServerConfig

STATUS_PRIORITY = ['Failure.Building', 'Failure.Sleeping', 'Failure.CheckingModifications',
                   'Success.Building', 'Success.Sleeping', 'Success.CheckingModifications',
                   'Unknown.Building', 'Unknown.Sleeping', 'Unknown.CheckingModifications', 'Unknown.Unknown']


class OverallIntegrationStatus(object):
    def __init__(self, servers: List[FilteredContinuousIntegrationServer]):
        self.servers = servers

    def get_build_status(self) -> Optional[str]:
        build_status_mapping = self.to_map()
        for status in STATUS_PRIORITY:
            if build_status_mapping[status]:
                return status
        return None

    def get_failing_builds(self) -> List[Project]:
        return [p for p in self.get_projects() if p.effective_status() == 'Failure']

    def to_map(self) -> Dict[str, List[Project]]:
        status: Dict[str, List[Project]] = {key: [] for key in STATUS_PRIORITY}
        for project in self.get_projects():
            if project.get_build_status() in status:
                status[project.get_build_status()].append(project)
            else:
                status['Unknown.Unknown'].append(project)
        return status

    def get_projects(self) -> List[Project]:
        all_projects = []
        for server in self.servers:
            if server.get_projects() is not None:
                all_projects.extend(server.get_projects())
        return all_projects

    def unavailable_servers(self) -> List[FilteredContinuousIntegrationServer]:
        return [server for server in self.servers if server.unavailable]


class ProjectsPopulator(QThread):
    updated_projects = QtCore.pyqtSignal(object)

    def __init__(self, config: Config, parent: QObject = None):
        QThread.__init__(self, parent)
        self.config = config
        self.server_configs: List[ServerConfig] = []
        self.timeout: Optional[float] = None
        self.last_known: Dict[str, List[Project]] = {}
        self.reload_pending = False
        self.finished.connect(self.on_finished)

    def load_from_server(self):
        if self.isRunning():
            return
        self.server_configs = self.config.get_server_configs()
        self.timeout = self.config.timeout
        self.start()

    def reload(self):
        self.reload_pending = self.isRunning()
        self.load_from_server()

    def on_finished(self):
        if self.reload_pending:
            self.reload_pending = False
            self.load_from_server()

    def process(self, server_configs: List[ServerConfig]):
        overall_status = []
        for server_config in server_configs:
            overall_status.append(self.check_nodes(server_config))
        self.updated_projects.emit(OverallIntegrationStatus(overall_status))

    def run(self):
        self.process(self.server_configs)

    def check_nodes(self, server_config: ServerConfig) -> FilteredContinuousIntegrationServer:
        server = self.with_last_known(ProjectLoader(server_config, self.timeout).get_data().server)
        return FilteredContinuousIntegrationServer(server, server_config.excluded_projects)

    def with_last_known(self, server: ContinuousIntegrationServer) -> ContinuousIntegrationServer:
        if server.unavailable:
            return ContinuousIntegrationServer(server.url, self.last_known.get(server.url, []), True)
        self.last_known[server.url] = server.get_projects()
        return server


class ProjectLoader(object):
    def __init__(self, server_config: ServerConfig, timeout: Optional[float], connection=HttpConnection()):
        self.server_config = server_config
        self.timeout = timeout
        self.connection = connection

    def get_data(self) -> Response:
        print("checking %s" % self.server_config.url)
        try:
            headers = {}
            if self.server_config.authentication_type == ServerConfig.AUTH_BEARER_TOKEN:
                headers['Authorization'] = 'Bearer %s' % self.server_config.password

            data = self.connection.connect(self.server_config, self.timeout, headers)
            projects = self.parse(data)
        except Exception as ex:
            print(ex)
            return Response(ContinuousIntegrationServer(self.server_config.url, [], True), ex)
        print("processed %s" % self.server_config.url)
        return Response(ContinuousIntegrationServer(self.server_config.url, projects))

    def parse(self, data) -> List[Project]:
        dom = minidom.parseString(data)
        root = dom.documentElement.tagName
        if root != 'Projects':
            raise ValueError('Not a cctray feed: expected <Projects> as the root element, got <%s>' % root)
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
        return projects
