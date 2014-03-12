import pytz

from PyQt4 import QtCore
from PyQt4.QtCore import Qt
from PyQt4 import QtGui
from buildnotifylib.generated.server_configuration_ui import Ui_serverConfigurationDialog
from buildnotifylib.core.timed_event import BackgroundEvent
from buildnotifylib.core.projects import ProjectLoader


class ServerConfigurationDialog(QtGui.QDialog):
    def __init__(self, editable, url, conf, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_serverConfigurationDialog()
        self.ui.setupUi(self)
        self.editable = editable
        self.ui.addServerUrl.setText(url)
        self.conf = conf
        timezones = QtCore.QStringList(pytz.all_timezones)
        self.ui.timezoneList.addItems(timezones)

        self.ui.timezoneList.setCurrentIndex(timezones.indexOf(self.conf.get_timezone(self.server_url())))

        if not editable:
            self.auto_load()
        self.connect(self.ui.loadUrlButton, QtCore.SIGNAL("clicked()"), self.fetch_data)

    def auto_load(self):
        self.ui.addServerUrl.setReadOnly(True)
        self.ui.loadUrlButton.setEnabled(False)
        self.fetch_data()

    def fetch_data(self):
        self.ui.loadUrlButton.setEnabled(False)
        self.event = BackgroundEvent(self.load_projects, self)
        self.connect(self.event, QtCore.SIGNAL('complete'), lambda data: self.load_data(data))
        self.event.start()

    def load_projects(self):
        self.project_loader = ProjectLoader(self.server_url(), self.conf.timeout)
        return self.project_loader.get_data()

    def load_data(self, server):
        self.ui.loadUrlButton.setEnabled(self.editable)
        excluded_projects = self.conf.get_project_excludes(self.server_url())

        projects_model = QtGui.QStandardItemModel()
        for project in server.projects:
            item = QtGui.QStandardItem(project.name)
            item.setCheckable(True)
            check = Qt.Unchecked if project.name in excluded_projects else Qt.Checked
            item.setCheckState(check)
            projects_model.appendRow(item)
        self.ui.projectsList.setModel(projects_model)

    def server_url(self):
        return str(self.ui.addServerUrl.text())

    def save(self):
        projects_model = self.ui.projectsList.model()
        if projects_model is None:
            return self.server_url()
        excluded_projects = [str(projects_model.index(index, 0).data().toString()) for index in range(projects_model.rowCount()) if projects_model.index(index, 0).data(Qt.CheckStateRole) == Qt.Unchecked]
        self.conf.set_project_excludes(self.server_url(), excluded_projects)
        self.conf.set_project_timezone(self.server_url(), self.ui.timezoneList.currentText())
        return self.server_url()

