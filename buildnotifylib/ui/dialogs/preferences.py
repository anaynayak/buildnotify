from dataclasses import replace

from PySide6.QtCore import QEvent, QModelIndex, QObject, QPersistentModelIndex, QStringListModel, Qt
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QDialog, QWidget

from buildnotifylib.core.ports import Connection
from buildnotifylib.core.settings import AppSettings, ServerSettings, SortKey
from buildnotifylib.generated.preferences_ui import Ui_Preferences
from buildnotifylib.ui.dialogs.server_configuration_dialog import ServerConfigurationDialog

ENTER_KEYS = (Qt.Key.Key_Return, Qt.Key.Key_Enter)


class PreferencesDialog(QDialog):
    def __init__(
        self,
        settings: AppSettings,
        connection: Connection,
        parent: QWidget | None = None,
        keystore_available: bool = True,
    ):
        super().__init__(parent)
        self.keystore_available = keystore_available
        self.settings = settings
        self.connection = connection
        self.servers = {server.url: server for server in settings.servers}
        self.ui = Ui_Preferences()
        self.ui.setupUi(self)
        self.checkboxes = dict(
            successfulBuild=self.ui.successfulBuildsCheckbox,
            brokenBuild=self.ui.brokenBuildsCheckbox,
            fixedBuild=self.ui.fixedBuildsCheckbox,
            stillFailingBuild=self.ui.stillFailingBuildsCheckbox,
            connectivityIssues=self.ui.connectivityIssuesCheckbox,
            lastBuildTimeForProject=self.ui.showLastBuildTimeCheckbox,
        )
        self.set_values_from_config()

        # Connect up the buttons.
        self.ui.addButton.clicked.connect(self.add_server)
        self.ui.removeButton.clicked.connect(self.remove_element)
        self.ui.buttonBox.accepted.connect(self.accept)
        self.ui.configureProjectButton.clicked.connect(self.configure_projects)

    def set_values_from_config(self):
        self.set_urls(list(self.servers))
        self.ui.cctrayPathList.doubleClicked.connect(self.configure_projects)
        self.ui.cctrayPathList.installEventFilter(self)

        for key, checkbox in self.checkboxes.items():
            checkbox.setChecked(self.settings.notify(key))

        self.ui.pollingIntervalSpinBox.setValue(self.settings.interval_seconds)
        self.ui.scriptCheckbox.setChecked(self.settings.custom_script_enabled)
        self.ui.scriptLineEdit.setText(self.settings.custom_script)
        self.ui.sortBuildByLastBuildTime.setChecked(self.settings.sort_key is SortKey.LAST_BUILD_TIME)
        self.ui.sortBuildByName.setChecked(self.settings.sort_key is SortKey.NAME)
        self.ui.showLastBuildLabelCheckbox.setChecked(self.settings.show_last_build_label)
        self.ui.symbolicIconsCheckbox.setChecked(self.settings.symbolic_icons)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is self.ui.cctrayPathList and is_enter(event):
            self.configure_projects()
            return True
        return super().eventFilter(watched, event)

    def set_urls(self, urls: list[str]):
        self.ui.cctrayPathList.setModel(QStringListModel(urls))
        self.ui.cctrayPathList.selectionModel().currentChanged.connect(self.current_changed)
        self.current_changed(QModelIndex())

    def current_changed(self, current: QModelIndex | QPersistentModelIndex, _previous=None):
        self.ui.configureProjectButton.setEnabled(current.isValid())

    def add_server(self):
        server = self.open_server_dialog(None)
        if server is None or server.url in self.get_urls():
            return
        self.servers[server.url] = server
        urls = self.ui.cctrayPathList.model().stringList()
        urls.append(server.url)
        self.set_urls(urls)

    def remove_element(self):
        index = self.ui.cctrayPathList.selectionModel().currentIndex()
        if not index.isValid():
            return
        urls = self.ui.cctrayPathList.model().stringList()
        urls.pop(index.row())
        self.set_urls(urls)

    def configure_projects(self):
        index = self.ui.cctrayPathList.selectionModel().currentIndex()
        url = index.data()
        if not url:
            return
        server = self.open_server_dialog(self.servers.get(url, ServerSettings(url)))
        if server is None or self.duplicates_another(url, server.url):
            return
        self.servers[server.url] = server
        self.ui.cctrayPathList.model().setData(index, server.url)

    def duplicates_another(self, url: str, edited_url: str) -> bool:
        return edited_url != url and edited_url in self.get_urls()

    def open_server_dialog(self, server: ServerSettings | None) -> ServerSettings | None:
        dialog = ServerConfigurationDialog(
            server, self.settings.timeout_seconds, self.connection, self, keystore_available=self.keystore_available
        )
        edited = dialog.open()
        dialog.deleteLater()
        return edited

    def get_urls(self) -> list[str]:
        return self.ui.cctrayPathList.model().stringList()

    def get_selections(self) -> dict[str, bool]:
        return {key: checkbox.isChecked() for key, checkbox in self.checkboxes.items()}

    def sort_key(self) -> SortKey:
        return SortKey.NAME if self.ui.sortBuildByName.isChecked() else SortKey.LAST_BUILD_TIME

    def edited_settings(self) -> AppSettings:
        return replace(
            self.settings,
            servers=[self.servers[url] for url in self.get_urls()],
            interval_seconds=self.ui.pollingIntervalSpinBox.value(),
            custom_script=self.ui.scriptLineEdit.text(),
            custom_script_enabled=self.ui.scriptCheckbox.isChecked(),
            sort_key=self.sort_key(),
            show_last_build_label=self.ui.showLastBuildLabelCheckbox.isChecked(),
            symbolic_icons=self.ui.symbolicIconsCheckbox.isChecked(),
            notifications=self.get_selections(),
        )

    def open(self) -> AppSettings | None:  # type: ignore
        if self.exec() == QDialog.DialogCode.Accepted:
            return self.edited_settings()
        return None


def is_enter(event: QEvent) -> bool:
    return isinstance(event, QKeyEvent) and event.type() == QEvent.Type.KeyPress and event.key() in ENTER_KEYS
