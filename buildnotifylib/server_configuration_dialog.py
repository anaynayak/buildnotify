from zoneinfo import available_timezones

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QDialog, QMessageBox, QWidget

from buildnotifylib.adapters.http import is_ssl_error
from buildnotifylib.core.background_event import BackgroundEvent
from buildnotifylib.core.keystore import Keystore
from buildnotifylib.core.model import NONE_TIMEZONE, ServerSnapshot
from buildnotifylib.core.projects import ProjectLoader
from buildnotifylib.core.settings import ServerSettings
from buildnotifylib.generated.server_configuration_ui import Ui_serverConfigurationDialog


class ServerConfigurationDialog(QDialog):
    def __init__(self, server: ServerSettings | None, timeout: int, parent: QWidget | None = None):
        QDialog.__init__(self, parent)
        self.ui = Ui_serverConfigurationDialog()
        self.ui.setupUi(self)

        self.timeout = timeout
        self.projects_list = QtGui.QStandardItem("All")
        all_timezones = [NONE_TIMEZONE]
        all_timezones.extend(sorted(available_timezones()))
        self.ui.timezoneList.addItems(all_timezones)

        if server is not None:
            self.server = server
            self.ui.addServerUrl.setText(server.url)
            self.ui.timezoneList.setCurrentIndex(max(self.ui.timezoneList.findText(self.server.timezone), 0))
            self.ui.displayPrefix.setText(self.server.prefix)
            self.ui.username.setText(self.server.username)
            self.ui.password.setText(self.server.password)
            self.ui.authentication_type.setCurrentIndex(self.server.authentication_type)
            self.ui.usernameLabel.setVisible(self.server.authentication_type == self.server.AUTH_USERNAME_PASSWORD)
            self.ui.username.setVisible(self.server.authentication_type == self.server.AUTH_USERNAME_PASSWORD)
        else:
            self.server = ServerSettings("", timezone="")

        self.ui.loadUrlButton.clicked.connect(self.fetch_data)

        if not Keystore.is_available():
            self.ui.authenticationSettings.setTitle("Authentication (keyring dependency missing)")
            self.ui.authentication_type.setEnabled(False)
            self.ui.username.setEnabled(False)
            self.ui.password.setEnabled(False)

        self.ui.authentication_type.currentIndexChanged.connect(self.set_authentication_type)
        self.ui.backButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.skip_ssl_verification = bool(self.server.skip_ssl_verification)

    def set_authentication_type(self, index: int):
        self.ui.username.setText("")
        self.ui.password.setText("")
        if ServerSettings.AUTH_USERNAME_PASSWORD == index:
            # Username/password selected
            self.ui.username.setVisible(True)
            self.ui.usernameLabel.setVisible(True)
            self.ui.passwordLabel.setText("Password")
            self.ui.password.setPlaceholderText(None)
        elif ServerSettings.AUTH_BEARER_TOKEN == index:
            # Bearer token selected
            self.ui.username.setVisible(False)
            self.ui.usernameLabel.setVisible(False)
            self.ui.passwordLabel.setText("Bearer token")
            self.ui.password.setPlaceholderText("Do not include the 'Bearer' keyword")
        else:
            raise NotImplementedError(
                f'Unsupported value: "{self.ui.authentication_type.currentText()}". An implementation is missing.'
            )

    def fetch_data(self):
        error = self.url_error()
        if error:
            QMessageBox.critical(self, "Invalid input", error)
            return

        self.ui.loadUrlButton.setEnabled(False)
        self.project_loader = ProjectLoader(self.get_server_config(), self.timeout, apply_excludes=False)
        self.event = BackgroundEvent(self.project_loader.get_data, self)
        self.event.completed.connect(self.load_data)
        self.event.start()

    def url_error(self) -> str | None:
        url = self.ui.addServerUrl.text()
        if "" == url:
            return "Path field cannot be empty."
        if not url.lower().startswith(("http://", "https://")):
            return "Only http:// and https:// URLs are supported."
        return None

    def load_data(self, response: ServerSnapshot):
        self.ui.loadUrlButton.setEnabled(True)

        if response.unavailable:
            self.handle_errors(response)
            return

        self.ui.stackedWidget.setCurrentIndex(1)
        projects_model = QtGui.QStandardItemModel()
        projects_model.itemChanged.connect(self.project_checked)
        projects_model.setHorizontalHeaderLabels(["Select Projects"])
        self.projects_list = QtGui.QStandardItem("All")
        self.projects_list.setCheckable(True)
        for project in response.projects:
            item = QtGui.QStandardItem(project.name)
            item.setCheckable(True)
            check = Qt.Unchecked if project.name in self.server.excluded_projects else Qt.Checked
            item.setCheckState(check)
            self.projects_list.appendRow(item)
        projects_model.appendRow(self.projects_list)
        self.ui.projectsList.setModel(projects_model)
        self.ui.projectsList.expandToDepth(1)
        self.ui.projectsList.setItemsExpandable(False)
        self.ui.projectsList.setRootIsDecorated(False)

    def qtText(self, txt: str) -> str:
        return Qt.convertFromPlainText(txt)  # type: ignore

    def handle_errors(self, response: ServerSnapshot):
        if is_ssl_error(response.error):
            reply = QMessageBox.question(
                self,
                "Failed to fetch projects",
                f"<b>SSL error, retry without verification?:</b> {self.qtText(str(response.error))}",
                QMessageBox.Yes,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                self.skip_ssl_verification = True
                self.fetch_data()
            return

        if response.unavailable:
            QMessageBox.critical(self, "Failed to fetch projects", f"<b>Error:</b> {self.qtText(str(response.error))}")

    def project_checked(self, item: QStandardItem):
        if item.hasChildren():
            for index in range(item.rowCount()):
                item.child(index, 0).setCheckState(item.checkState())

    def server_url(self) -> str:
        return str(self.ui.addServerUrl.text())

    def get_server_config(self) -> ServerSettings:
        projects_model = self.ui.projectsList.model()

        def project(i, model):
            return model.index(i, 0, self.projects_list.index())

        excluded_projects = [
            project(i, projects_model).data()
            for i in range(self.projects_list.rowCount())
            if project(i, projects_model).data(Qt.CheckStateRole) == Qt.Unchecked
        ]
        return ServerSettings(
            self.server_url(),
            excluded_projects,
            str(self.ui.timezoneList.currentText()),
            str(self.ui.displayPrefix.text()),
            str(self.ui.username.text()),
            str(self.ui.password.text()),
            self.skip_ssl_verification,
            int(self.ui.authentication_type.currentIndex()),
        )

    def open(self) -> ServerSettings | None:  # type: ignore
        if self.exec_() == QDialog.Accepted:
            return self.get_server_config()
        return None
