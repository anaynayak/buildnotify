from PySide6.QtCore import QEvent, QModelIndex, QObject, QPersistentModelIndex, QStringListModel, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QAbstractItemView, QHBoxLayout, QListView, QPushButton, QVBoxLayout, QWidget

from buildnotifylib.core.ports import Connection
from buildnotifylib.core.settings import ServerSettings
from buildnotifylib.ui.dialogs.server.dialog import ServerConfigurationDialog
from buildnotifylib.ui.widgets.forms import section

ENTER_KEYS = (Qt.Key.Key_Return, Qt.Key.Key_Enter)


class ServersPage(QWidget):
    """The monitored servers, with buttons to add, remove and configure them."""

    def __init__(
        self,
        timeout: int,
        connection: Connection,
        keystore_available: bool = True,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self.timeout = timeout
        self.connection = connection
        self.keystore_available = keystore_available
        self.servers: dict[str, ServerSettings] = {}
        self.server_list = QListView()
        self.server_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.configure_button = QPushButton(self.tr("Configure"))
        self.remove_button = self.small_button("-", self.tr("Remove"))
        self.add_button = self.small_button("+", self.tr("Add"))

        buttons = QHBoxLayout()
        buttons.addStretch()
        for button in (self.configure_button, self.remove_button, self.add_button):
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

    @staticmethod
    def small_button(text: str, tooltip: str) -> QPushButton:
        button = QPushButton(text)
        button.setToolTip(tooltip)
        return button

    def set_value(self, servers: list[ServerSettings]) -> None:
        self.servers = {server.url: server for server in servers}
        self.set_urls(list(self.servers))

    def value(self) -> list[ServerSettings]:
        return [self.servers[url] for url in self.get_urls()]

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.server_list and is_enter(event):
            self.configure_projects()
            return True
        return super().eventFilter(watched, event)

    def set_urls(self, urls: list[str]) -> None:
        self.server_list.setModel(QStringListModel(urls))
        self.server_list.selectionModel().currentChanged.connect(self.current_changed)
        self.current_changed(QModelIndex())

    def current_changed(self, current: QModelIndex | QPersistentModelIndex, _previous=None) -> None:
        self.configure_button.setEnabled(current.isValid())

    def model(self) -> QStringListModel:
        return self.server_list.model()  # type: ignore[return-value]

    def get_urls(self) -> list[str]:
        return self.model().stringList()

    def add_server(self) -> None:
        server = self.open_server_dialog(None)
        if server is None or server.url in self.get_urls():
            return
        self.servers[server.url] = server
        self.set_urls([*self.get_urls(), server.url])

    def remove_element(self) -> None:
        index = self.server_list.selectionModel().currentIndex()
        if not index.isValid():
            return
        urls = self.get_urls()
        urls.pop(index.row())
        self.set_urls(urls)

    def configure_projects(self) -> None:
        index = self.server_list.selectionModel().currentIndex()
        url = index.data()
        if not url:
            return
        server = self.open_server_dialog(self.servers.get(url, ServerSettings(url)))
        if server is None or self.duplicates_another(url, server.url):
            return
        self.servers[server.url] = server
        self.model().setData(index, server.url)

    def duplicates_another(self, url: str, edited_url: str) -> bool:
        return edited_url != url and edited_url in self.get_urls()

    def open_server_dialog(self, server: ServerSettings | None) -> ServerSettings | None:
        dialog = ServerConfigurationDialog(
            server, self.timeout, self.connection, self.window(), keystore_available=self.keystore_available
        )
        edited = dialog.open()
        dialog.deleteLater()
        return edited


def is_enter(event: QEvent) -> bool:
    return isinstance(event, QKeyEvent) and event.type() == QEvent.Type.KeyPress and event.key() in ENTER_KEYS
