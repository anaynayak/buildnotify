from PyQt5 import QtCore
from PyQt5.QtCore import QObject, QThread

from buildnotifylib.adapters.settings_store import SettingsStore
from buildnotifylib.core.aggregate import OverallIntegrationStatus
from buildnotifylib.core.model import Project, ServerSnapshot
from buildnotifylib.core.ports import Connection
from buildnotifylib.core.projects import ProjectLoader
from buildnotifylib.core.settings import ServerSettings


class ProjectsPopulator(QThread):
    updated_projects = QtCore.pyqtSignal(object)

    def __init__(self, store: SettingsStore, connection: Connection, parent: QObject | None = None):
        QThread.__init__(self, parent)
        self.store = store
        self.connection = connection
        self.server_configs: list[ServerSettings] = []
        self.timeout: float | None = None
        self.last_known: dict[str, tuple[Project, ...]] = {}
        self.reload_pending = False
        self.finished.connect(self.on_finished)

    def load_from_server(self):
        if self.isRunning():
            return
        self.server_configs = list(self.store.settings.servers)
        self.timeout = self.store.settings.timeout_seconds
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
        snapshot = ProjectLoader(server_config, self.timeout, self.connection).get_data()
        return self.with_last_known(snapshot, server_config.excluded_projects)

    def with_last_known(self, snapshot: ServerSnapshot, excluded: list[str]) -> ServerSnapshot:
        if snapshot.unavailable:
            cached = tuple(p for p in self.last_known.get(snapshot.url, ()) if p.name not in excluded)
            return ServerSnapshot(snapshot.url, cached, snapshot.error)
        self.last_known[snapshot.url] = snapshot.projects
        return snapshot
