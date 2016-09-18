import pytz

from PyQt4 import QtCore
from PyQt4.QtCore import Qt
from PyQt4 import QtGui
from buildnotifylib.generated.server_configuration_ui import Ui_serverConfigurationDialog
from buildnotifylib.core.timed_event import BackgroundEvent
from buildnotifylib.core.projects import ProjectLoader
from serverconfig import ServerConfig


class ServerConfigurationDialog(QtGui.QDialog):
    def __init__(self, url, conf, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_serverConfigurationDialog()
        self.ui.setupUi(self)
        self.ui.addServerUrl.setText(url)
        self.conf = conf
        self.parent = QtGui.QStandardItem("All")
        timezones = QtCore.QStringList(pytz.all_timezones)
        self.ui.timezoneList.addItems(timezones)
        self.server = conf.get_server_config(url)
        self.ui.timezoneList.setCurrentIndex(timezones.indexOf(self.server.timezone))
        self.ui.displayPrefix.setText(self.server.prefix)
        self.ui.loadUrlButton.clicked.connect(self.fetch_data)
        self.ui.username.setText(self.server.username)
        self.ui.password.setText(self.server.password)
        self.ui.backButton.clicked.connect(lambda: self.ui.stackedWidget.setCurrentIndex(0))
        self.skip_ssl_verification = False

    def fetch_data(self):
        self.ui.loadUrlButton.setEnabled(False)
        self.event = BackgroundEvent(self.load_projects, self)
        self.connect(self.event, QtCore.SIGNAL('complete'), lambda data: self.load_data(data))
        self.event.start()

    def load_projects(self):
        self.project_loader = ProjectLoader(self.get_server_config(), self.conf.timeout)
        return self.project_loader.get_data()

    def load_data(self, response):
        self.ui.loadUrlButton.setEnabled(True)
        if response.failed():
            self.handle_errors(response)
            return

        self.ui.stackedWidget.setCurrentIndex(1)
        projects_model = QtGui.QStandardItemModel()
        projects_model.itemChanged.connect(self.project_checked)
        projects_model.setHorizontalHeaderLabels(['Select Projects'])
        self.parent = QtGui.QStandardItem("All")
        self.parent.setCheckable(True)
        for project in response.server.projects:
            item = QtGui.QStandardItem(project.name)
            item.setCheckable(True)
            check = Qt.Unchecked if project.name in self.server.excluded_projects else Qt.Checked
            item.setCheckState(check)
            self.parent.appendRow(item)
        projects_model.appendRow(self.parent)
        self.ui.projectsList.setModel(projects_model)
        self.ui.projectsList.expandToDepth(1)
        self.ui.projectsList.setItemsExpandable(False)
        self.ui.projectsList.setRootIsDecorated(False)

    def handle_errors(self, response):
        if response.ssl_error():
            reply = QtGui.QMessageBox.question(self, "Failed to fetch projects",
                                               "<b>SSL error, retry without verification?:</b> %s" % Qt.convertFromPlainText(str(response.error)),
                                               QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                self.skip_ssl_verification = True
                self.fetch_data()
            return

        if response.failed():
            QtGui.QMessageBox.critical(self, "Failed to fetch projects",
                                       "<b>Error:</b> %s" % Qt.convertFromPlainText(str(response.error)))
            return

    def project_checked(self, item):
        if item.hasChildren():
            [item.child(index, 0).setCheckState(item.checkState()) for index in range(item.rowCount())]

    def server_url(self):
        return str(self.ui.addServerUrl.text())

    def get_server_config(self):
        projects_model = self.ui.projectsList.model()

        def project(i, model):
            return model.index(i, 0, self.parent.index())

        excluded_projects = [str(project(i, projects_model).data().toString()) for i in range(self.parent.rowCount()) if
                             project(i, projects_model).data(Qt.CheckStateRole) == Qt.Unchecked]
        return ServerConfig(self.server_url(), excluded_projects,
                            str(self.ui.timezoneList.currentText()), str(self.ui.displayPrefix.text()),
                            str(self.ui.username.text()), str(self.ui.password.text()), self.skip_ssl_verification)

    def save(self):
        self.conf.save_server_config(self.get_server_config())
        return self.server_url()
