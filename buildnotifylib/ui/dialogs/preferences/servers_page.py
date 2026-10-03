from collections.abc import Callable
from urllib.parse import urlparse

from PySide6.QtCore import QEvent, QModelIndex, QObject, QPersistentModelIndex, QStringListModel, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QListView,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from buildnotifylib.core.ports import Connection
from buildnotifylib.core.settings import ServerSettings, SourceKind
from buildnotifylib.ui.dialogs.server.dialog import ServerConfigurationDialog
from buildnotifylib.ui.widgets.forms import section


class ServersPage(QWidget):
    """The monitored servers, with buttons to add, remove and configure them."""

    def __init__(
        self,
        timeout: int,
        connection: Connection,
        keystore_available: bool = True,
        parent: QWidget | None = None,
        project_counts: dict[str, int] | None = None,
    ):
        super().__init__(parent)
        self.timeout = timeout
        self.connection = connection
        self.keystore_available = keystore_available
        self.project_counts = project_counts or {}
        self.servers: dict[str, ServerSettings] = {}
        self.server_list = QListView()
        self.server_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.add_button = QPushButton(self.tr("A&dd..."))
        self.configure_button = QPushButton(self.tr("&Edit..."))
        self.remove_button = QPushButton(self.tr("&Remove"))

        buttons = QHBoxLayout()
        buttons.addStretch()
        for button in (self.add_button, self.configure_button, self.remove_button):
            buttons.addWidget(button)
        servers = QVBoxLayout()
        servers.addWidget(self.server_list)
        servers.addLayout(buttons)
        QVBoxLayout(self).addWidget(section(self.tr("Monitored servers"), servers))

        self.server_list.doubleClicked.connect(self.configure_projects)
        self.server_list.installEventFilter(self)
        self.add_button.clicked.connect(self.add_server)
        self.remove_button.clicked.connect(self.remove_element)
        self.configure_button.clicked.connect(self.configure_projects)

    def set_value(self, servers: list[ServerSettings]) -> None:
        self.servers = {server.url: server for server in servers}
        self.refresh()

    def value(self) -> list[ServerSettings]:
        return list(self.servers.values())

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.server_list and isinstance(event, QKeyEvent) and event.type() == QEvent.Type.KeyPress:
            action = self.key_actions().get(event.key())
            if action is not None:
                action()
                return True
        return super().eventFilter(watched, event)

    def key_actions(self) -> dict[int, Callable[[], None]]:
        return {
            Qt.Key.Key_Insert: self.add_server,
            Qt.Key.Key_Return: self.configure_projects,
            Qt.Key.Key_Enter: self.configure_projects,
            Qt.Key.Key_Delete: self.remove_element,
        }

    def refresh(self) -> None:
        rows = [row_text(server, self.project_counts.get(url)) for url, server in self.servers.items()]
        self.server_list.setModel(QStringListModel(rows))
        self.server_list.selectionModel().currentChanged.connect(self.current_changed)
        self.current_changed(QModelIndex())

    def current_changed(self, current: QModelIndex | QPersistentModelIndex, _previous=None) -> None:
        self.configure_button.setEnabled(current.isValid())
        self.remove_button.setEnabled(current.isValid())

    def model(self) -> QStringListModel:
        return self.server_list.model()  # type: ignore[return-value]

    def get_urls(self) -> list[str]:
        return list(self.servers)

    def current_url(self) -> str | None:
        row = self.server_list.selectionModel().currentIndex().row()
        urls = self.get_urls()
        return urls[row] if 0 <= row < len(urls) else None

    def add_server(self) -> None:
        server = self.open_server_dialog(None)
        if server is None or server.url in self.servers:
            return
        self.servers[server.url] = server
        self.refresh()

    def remove_element(self) -> None:
        url = self.current_url()
        if url is None or not self.confirm_removal(self.servers[url]):
            return
        del self.servers[url]
        self.refresh()

    def confirm_removal(self, server: ServerSettings) -> bool:
        answer = QMessageBox.question(
            self.window(), self.tr("Remove server"), self.tr("Remove %1?").replace("%1", server_name(server))
        )
        return answer == QMessageBox.StandardButton.Yes

    def configure_projects(self) -> None:
        url = self.current_url()
        if url is None:
            return
        server = self.open_server_dialog(self.servers[url])
        if server is None or self.duplicates_another(url, server.url):
            return
        replaced = [server if key == url else old for key, old in self.servers.items()]
        self.servers = {each.url: each for each in replaced}
        self.refresh()

    def duplicates_another(self, url: str, edited_url: str) -> bool:
        return edited_url != url and edited_url in self.servers

    def open_server_dialog(self, server: ServerSettings | None) -> ServerSettings | None:
        dialog = ServerConfigurationDialog(
            server, self.timeout, self.connection, self.window(), keystore_available=self.keystore_available
        )
        edited = dialog.open()
        dialog.deleteLater()
        return edited


def server_name(server: ServerSettings) -> str:
    return server.prefix or urlparse(server.url).hostname or server.url


def server_target(server: ServerSettings) -> str:
    if server.kind is not SourceKind.GITHUB:
        return urlparse(server.url).netloc or server.url
    workflow = "@".join(part for part in (server.workflow, server.branch) if part)
    return " ".join(part for part in (server.repository, workflow) if part)


def row_text(server: ServerSettings, project_count: int | None = None) -> str:
    parts = [server_name(server), str(server.kind), server_target(server)]
    if project_count is not None:
        parts.append(f"{project_count} project" + ("" if project_count == 1 else "s"))
    return " - ".join(parts)
