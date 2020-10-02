from typing import Optional

import pytz
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem
from PyQt5.QtWidgets import QDialog, QMessageBox, QWidget

from buildnotifylib.config import Config
from buildnotifylib.core.background_event import BackgroundEvent
from buildnotifylib.core.keystore import Keystore
from buildnotifylib.core.projects import ProjectLoader
from buildnotifylib.core.response import Response
from buildnotifylib.generated.server_configuration_ui import Ui_serverConfigurationDialog
from buildnotifylib.serverconfig import ServerConfig


class ServerConfigurationDialog(QDialog):
    def __init__(self, url: Optional[str], conf: Config, parent: QWidget = None):
        QDialog.__init__(self, parent)
        self.ui = Ui_serverConfigurationDialog()
        self.ui.setupUi(self)

        self.conf = conf
        self.projects_list = QtGui.QStandardItem("All")
        all_timezones = [Config.NONE_TIMEZONE]
        all_timezones.extend(pytz.all_timezones)
        self.ui.timezoneList.addItems(all_timezones)

        if url is not None:
            self.ui.addServerUrl.setText(url)
            self.server = conf.get_server_config(url)
            self.ui.timezoneList.setCurrentIndex(all_timezones.index(self.server.timezone))
            self.ui.displayPrefix.setText(self.server.prefix)
            self.ui.username.setText(self.server.username)
            self.ui.password.setText(self.server.password)
            self.ui.authentication_type.setCurrentIndex(self.server.authentication_type)
            self.ui.usernameLabel.setVisible(self.server.authentication_type == self.server.AUTH_USERNAME_PASSWORD)
            self.ui.username.setVisible(self.server.authentication_type == self.server.AUTH_USERNAME_PASSWORD)
        else:
            self.server = ServerConfig('', [], '', '', '', '')

        self.ui.loadUrlButton.clicked.connect(self.fetch_data)

        if not Keystore.is_available():
            self.ui.authenticationSettings.setTitle('Authentication (keyring dependency missing)')
            self.ui.authentication_type.setEnabled(False)
            self.ui.username.setEnabled(False)
            self.ui.password.setEnabled(False)

        self.ui.authentication_type.currentIndexChanged.connect(self.set_authentication_type)
        self.ui.backButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.skip_ssl_verification = False

    def set_authentication_type(self, index: int):
        self.ui.username.setText('')
        self.ui.password.setText('')
        if ServerConfig.AUTH_USERNAME_PASSWORD == index:
            # Username/password selected
            self.ui.username.setVisible(True)
            self.ui.usernameLabel.setVisible(True)
            self.ui.passwordLabel.setText('Password')
            self.ui.password.setPlaceholderText(None)
        elif ServerConfig.AUTH_BEARER_TOKEN == index:
            # Bearer token selected
            self.ui.username.setVisible(False)
            self.ui.usernameLabel.setVisible(False)
            self.ui.passwordLabel.setText('Bearer token')
            self.ui.password.setPlaceholderText("Do not include the 'Bearer' keyword")
        else:
            raise NotImplemented('Unsupported value: "%s". An implementation is missing.'
                                 % self.ui.authentication_type.currentText())

    def fetch_data(self):
        if '' == self.ui.addServerUrl.text():
            QMessageBox.critical(self, "Invalid input", "Path field cannot be empty.")
            return

        self.ui.loadUrlButton.setEnabled(False)
        self.event = BackgroundEvent(self.load_projects, self)
        self.event.completed.connect(self.load_data)
        self.event.start()

    def load_projects(self) -> Response:
        config = self.get_server_config()
        self.project_loader = ProjectLoader(config, self.conf.timeout)
        return self.project_loader.get_data()

    def load_data(self, response: Response):
        self.ui.loadUrlButton.setEnabled(True)

        if response.failed():
            self.handle_errors(response)
            return

        self.ui.stackedWidget.setCurrentIndex(1)
        projects_model = QtGui.QStandardItemModel()
        projects_model.itemChanged.connect(self.project_checked)  # type: ignore
        projects_model.setHorizontalHeaderLabels(['Select Projects'])
        self.projects_list = QtGui.QStandardItem("All")
        self.projects_list.setCheckable(True)
        for project in response.server.projects:
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

    def handle_errors(self, response: Response):
        if response.ssl_error():
            reply = QMessageBox.question(self, "Failed to fetch projects",
                                         "<b>SSL error, retry without verification?:</b> %s" % self.qtText(
                                             str(response.error)),
                                         QMessageBox.Yes, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.skip_ssl_verification = True
                self.fetch_data()
            return

        if response.failed():
            QMessageBox.critical(self, "Failed to fetch projects",
                                 "<b>Error:</b> %s" % self.qtText(str(response.error)))

    def project_checked(self, item: QStandardItem):
        if item.hasChildren():
            for index in range(item.rowCount()):
                item.child(index, 0).setCheckState(item.checkState())

    def server_url(self) -> str:
        return str(self.ui.addServerUrl.text())

    def get_server_config(self) -> ServerConfig:
        projects_model = self.ui.projectsList.model()

        def project(i, model):
            return model.index(i, 0, self.projects_list.index())

        excluded_projects = [project(i, projects_model).data() for i in range(self.projects_list.rowCount()) if
                             project(i, projects_model).data(Qt.CheckStateRole) == Qt.Unchecked]
        return ServerConfig(self.server_url(), excluded_projects,
                            str(self.ui.timezoneList.currentText()), str(self.ui.displayPrefix.text()),
                            str(self.ui.username.text()), str(self.ui.password.text()), self.skip_ssl_verification,
                            int(self.ui.authentication_type.currentIndex()))

    def open(self) -> Optional[ServerConfig]:  # type: ignore
        if self.exec_() == QDialog.Accepted:
            return self.get_server_config()
        return None
