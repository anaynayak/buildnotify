from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QThread

from buildnotifylib.config import Config
from buildnotifylib.core import cctray
from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.http_connection import HttpConnection
from buildnotifylib.core.model import Project, ServerSnapshot
from buildnotifylib.core.settings import ServerSettings


class ProjectsPopulator(QThread):
    updated_projects = QtCore.pyqtSignal(object)

    def __init__(self, config: Config, parent: QObject | None = None):
        QThread.__init__(self, parent)
        self.config = config
        self.server_configs: list[ServerSettings] = []
        self.timeout: float | None = None
        self.last_known: dict[str, tuple[Project, ...]] = {}
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

    def process(self, server_configs: list[ServerSettings]):
        overall_status = []
        for server_config in server_configs:
            overall_status.append(self.check_nodes(server_config))
        self.updated_projects.emit(OverallIntegrationStatus(overall_status))

    def run(self):
        self.process(self.server_configs)

    def check_nodes(self, server_config: ServerSettings) -> ServerSnapshot:
        snapshot = ProjectLoader(server_config, self.timeout).get_data()
        return self.with_last_known(snapshot, server_config.excluded_projects)

    def with_last_known(self, snapshot: ServerSnapshot, excluded: list[str]) -> ServerSnapshot:
        if snapshot.unavailable:
            cached = tuple(p for p in self.last_known.get(snapshot.url, ()) if p.name not in excluded)
            return ServerSnapshot(snapshot.url, cached, snapshot.error)
        self.last_known[snapshot.url] = snapshot.projects
        return snapshot


class ProjectLoader:
    def __init__(
        self,
        server_config: ServerSettings,
        timeout: float | None,
        connection=HttpConnection(),
        apply_excludes: bool = True,
    ):
        self.server_config = server_config
        self.timeout = timeout
        self.connection = connection
        self.apply_excludes = apply_excludes

    def get_data(self) -> ServerSnapshot:
        print(f"checking {self.server_config.url}")
        try:
            headers = {}
            if self.server_config.authentication_type == ServerSettings.AUTH_BEARER_TOKEN:
                headers["Authorization"] = f"Bearer {self.server_config.password}"

            data = self.connection.connect(self.server_config, self.timeout, headers)
            projects = self.parse(data)
        except Exception as ex:
            print(ex)
            return ServerSnapshot(self.server_config.url, error=ex)
        print(f"processed {self.server_config.url}")
        return ServerSnapshot(self.server_config.url, tuple(projects))

    def parse(self, data: bytes) -> list[Project]:
        return cctray.parse(data, self.server_config, apply_excludes=self.apply_excludes)
